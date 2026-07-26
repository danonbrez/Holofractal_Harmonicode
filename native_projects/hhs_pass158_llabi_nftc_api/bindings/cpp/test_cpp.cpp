#include "hhs158.hpp"

#include <array>
#include <iostream>
#include <string>

int main() {
    using namespace hhs158;
    Context context;
    HHS158DefinitionDescriptor definition_descriptor{};
    initialize(definition_descriptor);
    const std::array<std::uint64_t, 2> shape{9, 9};
    definition_descriptor.contract_id = span("HHS-P158-LLABI-NFTC-API");
    definition_descriptor.schema_version = span("1.0.0");
    definition_descriptor.canonical_name = span("CPP_RAII_CONSTRAINT");
    definition_descriptor.object_class = span("NON_FUNGIBLE_TENSOR_CONSTRAINT");
    definition_descriptor.canonical_constraints = span("A==B==C;O!=Pi");
    definition_descriptor.symbol_table = span("A,B,C,O,Pi,x");
    definition_descriptor.numeric_policy = span("EXACT_SYMBOLIC");
    definition_descriptor.operator_policy = span("HHS_TYPED_OPERATORS");
    definition_descriptor.authority_root = span("PASS_158_INHERITED_ROOT");
    definition_descriptor.ancestry = span("P154|P155|P156|P156.1|P157");
    definition_descriptor.tensor_rank = static_cast<std::uint32_t>(shape.size());
    definition_descriptor.tensor_shape = shape.data();
    HHS158Definition *definition = nullptr;
    HHS158Receipt *definition_receipt = nullptr;
    check(hhs158_definition_register(context.get(), &definition_descriptor, &definition, &definition_receipt));

    HHS158InstanceConfig instance_config{};
    initialize(instance_config);
    instance_config.instance_nonce = span("cpp-raii-instance");
    instance_config.max_vm81_steps = 100000;
    instance_config.max_recursion_depth = 72;
    instance_config.max_state_bytes = 16777216;
    instance_config.max_receipt_bytes = 1048576;
    instance_config.projection_profile_mask = 0xffffffffu;
    HHS158Instance *instance = nullptr;
    HHS158Receipt *instance_receipt = nullptr;
    check(hhs158_instance_create(context.get(), definition, &instance_config, &instance, &instance_receipt));

    std::array<std::uint8_t, HHS158_HASH216_LENGTH> id_bytes{};
    HHS158MutableByteSpan id_output{id_bytes.data(), id_bytes.size(), 0};
    check(hhs158_instance_id(instance, &id_output));
    const std::string instance_id(reinterpret_cast<const char *>(id_bytes.data()), id_bytes.size());

    HHS158CapabilityRequest capability_request{};
    initialize(capability_request);
    capability_request.issuer = span("HHS_PASS158_AUTHORITY");
    capability_request.subject = span("cpp-binding");
    capability_request.application_id = span("org.hhs.pass158.cpp");
    capability_request.object_scope = span(instance_id);
    capability_request.operation_scope = HHS158_CAP_VALIDATE | HHS158_CAP_EXECUTE | HHS158_CAP_COMMIT | HHS158_CAP_REPLAY;
    capability_request.mutation_scope = HHS158_MUTATION_INSTANCE;
    capability_request.max_vm81_steps = 100000;
    capability_request.issued_at = 1799711700;
    capability_request.expires_at = 1799719999;
    HHS158Capability *capability = nullptr;
    check(hhs158_capability_open(context.get(), &capability_request, &capability));

    HHS158Value value{};
    initialize(value);
    value.kind = HHS158_VALUE_RATIONAL;
    value.flags = HHS158_FLAG_AUTHORITATIVE | HHS158_FLAG_IMMUTABLE;
    value.canonical_payload = span("1/3");
    check(hhs158_instance_bind(instance, span("x"), &value));

    HHS158ValidationPolicy validation{};
    initialize(validation);
    validation.max_recursion_depth = 72;
    validation.max_vm81_steps = 100000;
    HHS158ValidationReport report{};
    check(hhs158_instance_validate_static(instance, &validation, &report));

    HHS158Operation operation{};
    initialize(operation);
    operation.opcode = HHS158_OP_BIND_EQ;
    operation.operands = span("A,B");
    HHS158TransitionDescriptor transition_descriptor{};
    initialize(transition_descriptor);
    transition_descriptor.operations = &operation;
    transition_descriptor.operation_count = 1;
    transition_descriptor.expected_pre_state_root = span(std::string_view(report.state_root, HHS158_HASH216_LENGTH));
    transition_descriptor.max_vm81_steps = 1000;
    transition_descriptor.max_recursion_depth = 72;
    transition_descriptor.max_output_bytes = 1048576;
    HHS158Transition *transition = nullptr;
    check(hhs158_transition_create(instance, capability, &transition_descriptor, &transition));

    HHS158ExecutionOptions execution_options{};
    initialize(execution_options);
    execution_options.max_vm81_steps = 1000;
    execution_options.atomic_execute_and_commit = 1;
    HHS158ExecutionResult execution_result{};
    HHS158Receipt *commit_receipt = nullptr;
    check(hhs158_transition_execute(transition, &execution_options, &execution_result, &commit_receipt));
    if (std::string(execution_result.classification) != "HHS_VM81_TRANSITION_COMMITTED") return 2;

    HHS158ReplayOptions replay_options{};
    initialize(replay_options);
    replay_options.verify_hash72 = 1;
    replay_options.verify_hash216 = 1;
    replay_options.verify_semantic_root = 1;
    HHS158ReplayResult replay_result{};
    check(hhs158_receipt_replay(context.get(), commit_receipt, &replay_options, &replay_result));
    if (!replay_result.matched) return 3;

    Receipt receipt(commit_receipt);
    const auto serialized = receipt.serialize();
    if (serialized.find("HHS_P158_HASH72_EXECUTION_RECEIPT_CLOSED") == std::string::npos) return 4;
    std::cout << "HHS_PASS_158_CPP_BINDING_VERIFIED\n";
    return 0;
}
