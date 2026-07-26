use std::ffi::{c_char, c_void, CStr};
use std::ptr;

#[repr(C)]
#[derive(Clone, Copy)]
struct Header {
    struct_size: u32,
    struct_version: u32,
}

#[repr(C)]
struct ContextConfig {
    header: Header,
    abi_major: u32,
    abi_minor: u32,
    max_definitions: u32,
    max_instances: u32,
    max_receipts: u32,
    max_memory_bytes: u64,
    deterministic_epoch_seconds: u64,
    flags: u32,
    reserved: u32,
}

#[repr(C)]
struct MutableByteSpan {
    data: *mut u8,
    capacity: usize,
    size_written: usize,
}

#[link(name = "hhs_pass158")]
unsafe extern "C" {
    fn hhs158_abi_version_major() -> u32;
    fn hhs158_abi_version_minor() -> u32;
    fn hhs158_contract_id() -> *const c_char;
    fn hhs158_context_create(config: *const ContextConfig, output: *mut *mut c_void) -> i32;
    fn hhs158_context_release(context: *mut c_void);
    fn hhs158_capabilities_json(output: *mut MutableByteSpan) -> i32;
}

fn main() {
    unsafe {
        assert_eq!(hhs158_abi_version_major(), 1);
        assert_eq!(hhs158_abi_version_minor(), 0);
        let contract = CStr::from_ptr(hhs158_contract_id()).to_str().unwrap();
        assert_eq!(contract, "HHS-P158-LLABI-NFTC-API");

        let config = ContextConfig {
            header: Header {
                struct_size: std::mem::size_of::<ContextConfig>() as u32,
                struct_version: 1,
            },
            abi_major: 1,
            abi_minor: 0,
            max_definitions: 16,
            max_instances: 16,
            max_receipts: 32,
            max_memory_bytes: 16_777_216,
            deterministic_epoch_seconds: 1_799_711_799,
            flags: 0,
            reserved: 0,
        };
        let mut context: *mut c_void = ptr::null_mut();
        assert_eq!(hhs158_context_create(&config, &mut context), 0);
        assert!(!context.is_null());

        let mut first = MutableByteSpan {
            data: ptr::null_mut(),
            capacity: 0,
            size_written: 0,
        };
        assert_eq!(hhs158_capabilities_json(&mut first), 2);
        let mut bytes = vec![0u8; first.size_written];
        let mut second = MutableByteSpan {
            data: bytes.as_mut_ptr(),
            capacity: bytes.len(),
            size_written: 0,
        };
        assert_eq!(hhs158_capabilities_json(&mut second), 0);
        let text = std::str::from_utf8(&bytes[..second.size_written]).unwrap();
        assert!(text.contains("NON_FUNGIBLE_TENSOR_CONSTRAINT"));
        assert!(text.contains("Rust"));
        hhs158_context_release(context);
    }
    println!("HHS_PASS_158_RUST_BINDING_VERIFIED");
}
