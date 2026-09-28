from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "hhs_gui" / "rendering" / "hhs_harmonicode_three_webgl_v1.js"
LANE5 = ROOT / "applications" / "holofractal_harmonizer" / "lane5_holographic_sprite_5184.html"


def test_hhs3d_projection_authority_is_fail_closed():
    source = RUNTIME.read_text(encoding="utf-8")
    assert 'schema:"HHS_HARMONICODE_THREE_WEBGL_V1"' in source
    assert "canonicalMutationAuthority:false" in source
    assert "vm81AdmissionAuthority:false" in source
    assert "hash72CommitAuthority:false" in source
    assert "hash216IdentityAuthority:false" in source
    assert "gpuProjectionOnly:true" in source
    assert "rendererWritebackForbidden:true" in source
    assert 'getContext("webgl2"' in source
    assert "HHS3D_WEBGL2_REQUIRED" in source
    assert "WebSocket(" not in source
    assert "fetch(" not in source


def test_hhs3d_exports_lane5_three_compatible_surface():
    source = RUNTIME.read_text(encoding="utf-8")
    required = (
        "Vector2",
        "Vector3",
        "Scene",
        "PerspectiveCamera",
        "OrthographicCamera",
        "BufferAttribute",
        "BufferGeometry",
        "PlaneGeometry",
        "ShaderMaterial",
        "Points",
        "Mesh",
        "WebGLRenderTarget",
        "WebGLRenderer",
        "OrbitControls",
        "AdditiveBlending",
        "NoBlending",
        "RGBAFormat",
        "NearestFilter",
    )
    for symbol in required:
        assert symbol in source
    assert "gl.drawArrays(object.isPoints?gl.POINTS:gl.TRIANGLES" in source
    assert "gl.framebufferTexture2D" in source
    assert "gl.uniformMatrix4fv" in source
    assert "vertex300(source)" in source
    assert "fragment300(source)" in source


def test_lane5_uses_repository_native_hhs3d_not_threejs_cdn():
    html = LANE5.read_text(encoding="utf-8")
    assert "../../hhs_gui/rendering/hhs_harmonicode_three_webgl_v1.js" in html
    assert "new HHS3D.WebGLRenderer" in html
    assert "new HHS3D.Scene" in html
    assert "new HHS3D.ShaderMaterial" in html
    assert "new HHS3D.WebGLRenderTarget" in html
    assert "new HHS3D.OrbitControls" in html
    assert "THREE." not in html
    assert "cdnjs.cloudflare.com/ajax/libs/three.js" not in html
    assert "cdn.jsdelivr.net/npm/three" not in html
