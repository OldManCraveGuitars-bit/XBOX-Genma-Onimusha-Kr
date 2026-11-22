using System;
using System.IO;
using System.Threading;
using System.Windows.Forms;
using GenmaKorean;

// Calls the actual distributed assembly. No alternate patch implementation.
public static class VerifyPatcher {
    [STAThread] public static int Main(string[] args) {
        Console.SetOut(new StreamWriter(Console.OpenStandardOutput(), new System.Text.UTF8Encoding(false)) {AutoFlush=true});
        if(args.Length!=2) throw new ArgumentException("source.iso output.iso");
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        using(var form=new MainForm()) {
            if(!form.Text.EndsWith("v0.801")) throw new Exception("Wrong form version");
            foreach(Control control in form.Controls) {
                if(control.Left<0 || control.Top<0 || control.Right>form.ClientSize.Width || control.Bottom>form.ClientSize.Height)
                    throw new Exception("Control outside form: "+control.Text);
            }
        }
        string output=Path.GetFullPath(args[1]);
        if(File.Exists(output)) throw new Exception("Test output already exists");
        bool sawGeneration=false, cancelled=false;
        using(var token=new CancellationTokenSource()) {
            try {
                Engine.Apply(args[0],output,token.Token,(message,percent)=> {
                    if(message.Contains("생성 중")) { sawGeneration=true; token.Cancel(); }
                });
            } catch(OperationCanceledException) { cancelled=true; }
        }
        if(!sawGeneration || !cancelled || File.Exists(output)) throw new Exception("Cancellation failed");
        if(Directory.GetFiles(Path.GetDirectoryName(output),Path.GetFileName(output)+".*.partial").Length!=0)
            throw new Exception("Incomplete output remains");
        Console.WriteLine("{\"status\":\"passed\",\"form_controls_within_client_area\":true,\"cancel_during_actual_iso_generation\":true,\"partial_output_removed\":true}");
        return 0;
    }
}
