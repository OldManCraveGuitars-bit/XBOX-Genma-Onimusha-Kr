using System;
using System.IO;
using System.Reflection;
using System.Security.Cryptography;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Drawing;
using System.Web.Script.Serialization;

[assembly: AssemblyTitle("XBOX-Genma-Onimusha-Kr v0.8")]
[assembly: AssemblyDescription("환마 귀무자 일본판 ISO 한국어 패치")]
[assembly: AssemblyVersion("0.8.0.0")]
[assembly: AssemblyFileVersion("0.8.0.0")]

namespace GenmaKorean {
    public static class Engine {
        public const long SourceBytes=4905566208L, OutputBytes=5385351168L;
        public const string SourceHash="7f5af784f9b229c5d0061918e018a9052e328a5341efc7d9e1b5d36de5f58206";
        public const string OutputHash="dbd207078fc41095afe805743277676214fc6e71d2cce2db30f0b161dc0f8dc2";
        public static string Hex(byte[] bytes) { return BitConverter.ToString(bytes).Replace("-", "").ToLowerInvariant(); }
        public static string Hash(Stream stream,CancellationToken cancel,Action<int> progress) {
            stream.Position=0; byte[] block=new byte[4*1024*1024];
            using(var sha=SHA256.Create()) {
                int n; while((n=stream.Read(block,0,block.Length))>0) {
                    cancel.ThrowIfCancellationRequested(); sha.TransformBlock(block,0,n,block,0);
                    if(progress!=null) progress((int)(stream.Position*100/Math.Max(1,stream.Length)));
                }
                sha.TransformFinalBlock(new byte[0],0,0); return Hex(sha.Hash);
            }
        }
        public static string HashFile(string path) { using(var f=File.OpenRead(path)) return Hash(f,CancellationToken.None,null); }
        static string Extract(string resource,string destination,string expected) {
            using(var input=Assembly.GetExecutingAssembly().GetManifestResourceStream(resource)) {
                if(input==null) throw new InvalidDataException("내장 패치 리소스가 없습니다.");
                using(var output=new FileStream(destination,FileMode.CreateNew,FileAccess.Write,FileShare.None)) input.CopyTo(output);
            }
            if(HashFile(destination)!=expected) throw new InvalidDataException("내장 패치 파일의 SHA-256이 일치하지 않습니다.");
            return destination;
        }
        public static object Info() { return new {version="v0.8",source_bytes=SourceBytes,source_sha256=SourceHash,output_bytes=OutputBytes,output_sha256=OutputHash,patch_sha256=Resources.PatchHash,decoder_sha256=Resources.DecoderHash}; }
        public static object Apply(string sourcePath,string outputPath,CancellationToken cancel,Action<string,int> report) {
            sourcePath=Path.GetFullPath(sourcePath); outputPath=Path.GetFullPath(outputPath);
            if(String.Equals(sourcePath,outputPath,StringComparison.OrdinalIgnoreCase)) throw new IOException("원본과 출력 경로가 같습니다. 새 ISO 이름을 지정하세요.");
            if(File.Exists(outputPath)||Directory.Exists(outputPath)) throw new IOException("출력 경로가 이미 있습니다. 기존 파일은 덮어쓰지 않습니다.");
            if(!String.Equals(Path.GetExtension(outputPath),".iso",StringComparison.OrdinalIgnoreCase)) throw new IOException("결과 파일 확장자는 .iso여야 합니다.");
            if(!Directory.Exists(Path.GetDirectoryName(outputPath))) throw new IOException("출력 폴더가 없습니다.");
            string work=null,partial=null; Process decoder=null;
            try {
                using(var source=new FileStream(sourcePath,FileMode.Open,FileAccess.Read,FileShare.Read)) {
                    if(source.Length!=SourceBytes) throw new InvalidDataException("지원하지 않는 원본 크기입니다. Japan (En,Ja) 원본 ISO를 선택하세요.");
                    report("원본 ISO SHA-256 확인 중",0);
                    string actual=Hash(source,cancel,p=>report("원본 ISO SHA-256 확인 중",p*25/100));
                    if(actual!=SourceHash) throw new InvalidDataException("원본 SHA-256이 일치하지 않습니다.\n선택 파일: "+actual);
                    var drive=new DriveInfo(Path.GetPathRoot(outputPath));
                    if(drive.DriveFormat=="FAT32") throw new IOException("결과 ISO는 4GB를 넘습니다. NTFS 또는 exFAT 드라이브를 선택하세요.");
                    if(drive.AvailableFreeSpace<OutputBytes+64L*1024*1024) throw new IOException("출력 드라이브에 5.5GB 이상의 빈 공간이 필요합니다.");
                    cancel.ThrowIfCancellationRequested();
                    work=Path.Combine(Path.GetTempPath(),"GenmaKr-"+Guid.NewGuid().ToString("N")); Directory.CreateDirectory(work);
                    string executable=Extract("decoder",Path.Combine(work,"xdelta3.exe"),Resources.DecoderHash);
                    string patch=Extract("patch",Path.Combine(work,"v0.8.xdelta"),Resources.PatchHash);
                    partial=outputPath+"."+Guid.NewGuid().ToString("N")+".partial";
                    var start=new ProcessStartInfo(executable,"-d -D -R -s \""+sourcePath+"\" \""+patch+"\" \""+partial+"\"");
                    start.UseShellExecute=false; start.CreateNoWindow=true; start.RedirectStandardError=true;
                    start.EnvironmentVariables.Remove("XDELTA");
                    decoder=Process.Start(start); var errors=decoder.StandardError.ReadToEndAsync();
                    while(!decoder.WaitForExit(200)) {
                        if(cancel.IsCancellationRequested) { decoder.Kill(); decoder.WaitForExit(); cancel.ThrowIfCancellationRequested(); }
                        long bytes=File.Exists(partial)?new FileInfo(partial).Length:0;
                        report("일본판 → 한국어 ISO 생성 중",25+(int)(Math.Min(bytes,OutputBytes)*50/OutputBytes));
                    }
                    string detail=errors.GetAwaiter().GetResult();
                    if(decoder.ExitCode!=0) throw new InvalidDataException("패치 적용에 실패했습니다.\n"+detail);
                    decoder.Dispose(); decoder=null; cancel.ThrowIfCancellationRequested();
                    using(var output=new FileStream(partial,FileMode.Open,FileAccess.Read,FileShare.Read)) {
                        if(output.Length!=OutputBytes) throw new InvalidDataException("결과 ISO 크기가 일치하지 않습니다.");
                        actual=Hash(output,cancel,p=>report("결과 ISO SHA-256 확인 중",75+p*24/100));
                    }
                    if(actual!=OutputHash) throw new InvalidDataException("결과 ISO SHA-256이 일치하지 않습니다. 완성 파일로 저장하지 않습니다.");
                    cancel.ThrowIfCancellationRequested();
                    File.Move(partial,outputPath); partial=null;
                    report("완료 — 결과 ISO 해시가 일치합니다.",100);
                    return new {verified=true,version="v0.8",output=outputPath,bytes=OutputBytes,sha256=OutputHash,source_sha256=SourceHash};
                }
            } finally {
                if(decoder!=null) { if(!decoder.HasExited) { decoder.Kill(); decoder.WaitForExit(); } decoder.Dispose(); }
                if(partial!=null&&File.Exists(partial)) File.Delete(partial);
                if(work!=null&&Directory.Exists(work)) Directory.Delete(work,true);
            }
        }
    }

    public sealed class MainForm:Form {
        readonly TextBox source=new TextBox(),output=new TextBox();
        readonly Button browseSource=new Button(),browseOutput=new Button(),apply=new Button(),cancel=new Button();
        readonly Label status=new Label(); readonly ProgressBar progress=new ProgressBar();
        CancellationTokenSource cancellation; bool busy;
        public MainForm() {
            Text="환마 귀무자 한국어 패치 v0.8"; ClientSize=new Size(660,315); FormBorderStyle=FormBorderStyle.FixedDialog; MaximizeBox=false; StartPosition=FormStartPosition.CenterScreen;
            var title=new Label {Text="환마 귀무자 · Genma Onimusha",AutoSize=true,Location=new Point(20,18),Font=new Font(SystemFonts.MessageBoxFont.FontFamily,15,FontStyle.Bold)}; Controls.Add(title);
            Controls.Add(new Label {Text="Japan (En,Ja) 원본 ISO를 선택하세요. 원본과 기존 출력 파일은 보존합니다.",AutoSize=true,Location=new Point(20,56)});
            AddRow("원본 ISO",source,browseSource,88); AddRow("저장 위치",output,browseOutput,142);
            browseSource.Text=browseOutput.Text="찾아보기";
            browseSource.Click+=(s,e)=> { using(var d=new OpenFileDialog {Filter="Xbox ISO (*.iso)|*.iso",Title="일본판 원본 ISO 선택"}) if(d.ShowDialog()==DialogResult.OK) { source.Text=d.FileName; if(output.Text.Length==0) output.Text=Path.Combine(Path.GetDirectoryName(d.FileName),"XBOX-Genma-Onimusha-Kr-v0.8.iso"); } };
            browseOutput.Click+=(s,e)=> { using(var d=new SaveFileDialog {Filter="Xbox ISO (*.iso)|*.iso",FileName="XBOX-Genma-Onimusha-Kr-v0.8.iso",OverwritePrompt=true}) if(d.ShowDialog()==DialogResult.OK) output.Text=d.FileName; };
            status.SetBounds(20,197,620,25); status.Text="5.5GB 이상의 빈 공간이 필요합니다. Python 설치는 필요 없습니다."; Controls.Add(status);
            progress.SetBounds(20,226,620,18); Controls.Add(progress);
            apply.SetBounds(340,264,175,31); apply.Text="한글 패치 시작"; Controls.Add(apply);
            cancel.SetBounds(525,264,115,31); cancel.Text="취소"; cancel.Enabled=false; Controls.Add(cancel);
            cancel.Click+=(s,e)=> { if(cancellation!=null) { cancellation.Cancel(); status.Text="취소하는 중입니다..."; cancel.Enabled=false; } };
            apply.Click+=async(s,e)=>await StartApply();
            FormClosing+=(s,e)=> { if(busy) { e.Cancel=true; MessageBox.Show(this,"취소 버튼을 누르고 작업 종료를 기다려 주세요."); } };
        }
        void AddRow(string caption,TextBox box,Button button,int y) { Controls.Add(new Label {Text=caption,AutoSize=true,Location=new Point(20,y+4)}); box.SetBounds(100,y,440,25); button.SetBounds(548,y-1,92,28); Controls.Add(box); Controls.Add(button); }
        async Task StartApply() {
            string from=source.Text.Trim(),to=output.Text.Trim();
            if(from.Length==0||to.Length==0) { MessageBox.Show(this,"원본 ISO와 저장 위치를 지정하세요."); return; }
            busy=true; source.Enabled=output.Enabled=browseSource.Enabled=browseOutput.Enabled=apply.Enabled=false; cancel.Enabled=true; cancellation=new CancellationTokenSource();
            try {
                await Task.Run(()=>Engine.Apply(from,to,cancellation.Token,(text,percent)=>BeginInvoke((Action)(()=> { status.Text=text; progress.Value=Math.Max(0,Math.Min(100,percent)); }))));
                MessageBox.Show(this,"패치 완료. 결과 ISO의 SHA-256을 확인했습니다.\n"+to,"완료",MessageBoxButtons.OK,MessageBoxIcon.Information);
            } catch(OperationCanceledException) { status.Text="취소했습니다. 미완성 출력은 정리했습니다."; }
            catch(Exception ex) { status.Text="패치를 완료하지 못했습니다."; MessageBox.Show(this,ex.Message,"확인",MessageBoxButtons.OK,MessageBoxIcon.Error); }
            finally { busy=false; cancellation.Dispose(); cancellation=null; source.Enabled=output.Enabled=browseSource.Enabled=browseOutput.Enabled=apply.Enabled=true; cancel.Enabled=false; }
        }
    }
    public static class Program {
        [STAThread] public static int Main(string[] args) {
            try {
                if(args.Length>0) {
                    Console.SetOut(new StreamWriter(Console.OpenStandardOutput(),new System.Text.UTF8Encoding(false)) {AutoFlush=true});
                    Console.SetError(new StreamWriter(Console.OpenStandardError(),new System.Text.UTF8Encoding(false)) {AutoFlush=true});
                }
                var json=new JavaScriptSerializer();
                if(args.Length==1&&args[0]=="--info") { Console.WriteLine(json.Serialize(Engine.Info())); return 0; }
                if(args.Length==3&&args[0]=="--apply") { Console.WriteLine(json.Serialize(Engine.Apply(args[1],args[2],CancellationToken.None,(s,p)=>{}))); return 0; }
                if(args.Length!=0) throw new ArgumentException("사용법: --info 또는 --apply 원본.iso 결과.iso");
                Application.EnableVisualStyles(); Application.SetCompatibleTextRenderingDefault(false); Application.Run(new MainForm()); return 0;
            } catch(Exception ex) { Console.Error.WriteLine(ex.Message); return 1; }
        }
    }
}
