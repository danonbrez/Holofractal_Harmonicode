package org.hhs.pass158;

import java.math.BigInteger;

public final class Pass158JavaSmoke {
    public static void main(String[] args) {
        String capabilities = HHS158.capabilitiesJson();
        if (!capabilities.contains("NON_FUNGIBLE_TENSOR_CONSTRAINT")) {
            throw new IllegalStateException("capability descriptor missing object class");
        }
        String lifecycle = HHS158.nativeLifecycleSmoke();
        if (!lifecycle.equals("HHS_P158_NFT_TRANSITION_REPLAY_VERIFIED")) {
            throw new IllegalStateException("native lifecycle failed: " + lifecycle);
        }
        HHS158.ExactRational rational = new HHS158.ExactRational(
            new BigInteger("179971179971"), new BigInteger("1000000")
        );
        if (!rational.canonical().equals("179971179971/1000000")) {
            throw new IllegalStateException("exact rational drift");
        }
        boolean rejected = false;
        try {
            rational.toAuthoritativeDouble();
        } catch (UnsupportedOperationException expected) {
            rejected = true;
        }
        if (!rejected) throw new IllegalStateException("implicit double conversion accepted");
        System.out.println("HHS_PASS_158_JAVA_KOTLIN_JNI_BINDING_VERIFIED");
    }
}
