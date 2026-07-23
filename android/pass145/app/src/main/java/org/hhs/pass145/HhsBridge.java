package org.hhs.pass145;

import android.content.Context;
import android.content.SharedPreferences;
import android.webkit.JavascriptInterface;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.InetAddress;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;

public final class HhsBridge {
    private static final String PREFS = "hhs_pass145_api";
    private final Context context;

    HhsBridge(Context context) { this.context = context.getApplicationContext(); }

    @JavascriptInterface
    public String nativeStatus() { return NativeRuntime.statusJson(); }

    @JavascriptInterface
    public void configure(String endpoint, String token) throws Exception {
        URI uri = URI.create(endpoint);
        String host = uri.getHost();
        if (host == null || !(host.equals("127.0.0.1") || host.equals("localhost") || host.equals("::1"))) {
            throw new SecurityException("Only an authenticated loopback endpoint is admissible");
        }
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).edit()
                .putString("endpoint", endpoint.replaceAll("/+$", ""))
                .putString("token", token)
                .apply();
    }

    @JavascriptInterface
    public String request(String method, String path, String bodyJson) {
        try {
            SharedPreferences prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
            String endpoint = prefs.getString("endpoint", "http://127.0.0.1:8765");
            String token = prefs.getString("token", "");
            URL url = new URL(endpoint + path);
            InetAddress address = InetAddress.getByName(url.getHost());
            if (!address.isLoopbackAddress()) throw new SecurityException("Non-loopback route rejected");
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod(method);
            conn.setConnectTimeout(3000);
            conn.setReadTimeout(30000);
            conn.setRequestProperty("Authorization", "Bearer " + token);
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8");
            conn.setRequestProperty("Accept", "application/json");
            if (!method.equals("GET")) {
                conn.setDoOutput(true);
                byte[] body = bodyJson.getBytes(StandardCharsets.UTF_8);
                if (body.length > 16 * 1024 * 1024) throw new SecurityException("Request bound exceeded");
                try (OutputStream out = conn.getOutputStream()) { out.write(body); }
            }
            int status = conn.getResponseCode();
            InputStream input = status >= 400 ? conn.getErrorStream() : conn.getInputStream();
            StringBuilder result = new StringBuilder();
            try (BufferedReader reader = new BufferedReader(new InputStreamReader(input, StandardCharsets.UTF_8))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    result.append(line);
                    if (result.length() > 2_000_000) throw new SecurityException("Response bound exceeded");
                }
            }
            JSONObject envelope = new JSONObject();
            envelope.put("http_status", status);
            envelope.put("body", new JSONObject(result.toString()));
            return envelope.toString();
        } catch (Exception error) {
            try {
                JSONObject out = new JSONObject();
                out.put("ok", false);
                out.put("error_code", "RUNTIME_BINDING_MISMATCH");
                out.put("description", error.toString());
                return out.toString();
            } catch (Exception ignored) {
                return "{\"ok\":false,\"error_code\":\"RUNTIME_BINDING_MISMATCH\"}";
            }
        }
    }
}
