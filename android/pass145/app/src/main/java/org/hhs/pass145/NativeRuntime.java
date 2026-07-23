package org.hhs.pass145;

public final class NativeRuntime {
    static {
        System.loadLibrary("hhs_pass145");
    }
    private NativeRuntime() {}
    public static native String statusJson();
    public static native String hash72Witness(String label, String payload);
}
