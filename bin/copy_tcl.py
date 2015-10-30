import os, sys, subprocess

bin_dir = os.path.abspath(os.path.dirname(__file__))
env_dir = os.path.join(os.path.dirname(bin_dir), "env")

tcl_dest_dir = os.path.join(env_dir, "Lib", "tcl8.5")

if not os.path.exists(tcl_dest_dir):
    tcl_source_dir = os.path.join(sys.exec_prefix, "tcl", "tcl8.5")
    os.mkdir(tcl_dest_dir)
    subprocess.call(["xcopy", tcl_source_dir, tcl_dest_dir, "/S", "/E"])

tk_dest_dir = os.path.join(env_dir, "Lib", "tk8.5")

if not os.path.exists(tk_dest_dir):
    tk_source_dir = os.path.join(sys.exec_prefix, "tcl", "tk8.5")
    os.mkdir(tk_dest_dir)
    subprocess.call(["xcopy", tk_source_dir, tk_dest_dir, "/S", "/E"])
