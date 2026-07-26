package org.hhs.pass158;

import java.math.BigInteger;

public final class HHS158 {
    static {
        System.loadLibrary("hhs_pass158_jni");
    }

    private HHS158() {}

    public static native String capabilitiesJson();
    public static native String nativeLifecycleSmoke();

    public record ExactRational(BigInteger numerator, BigInteger denominator) {
        public ExactRational {
            if (denominator.signum() <= 0) {
                throw new IllegalArgumentException("denominator must be positive");
            }
            BigInteger gcd = numerator.gcd(denominator);
            numerator = numerator.divide(gcd);
            denominator = denominator.divide(gcd);
        }

        public String canonical() {
            return numerator + "/" + denominator;
        }

        public double toAuthoritativeDouble() {
            throw new UnsupportedOperationException("authoritative HHS rationals do not narrow to double");
        }
    }
}
