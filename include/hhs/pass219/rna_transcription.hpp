#pragma once

#include "cell_wall_membrane.hpp"

namespace hhs::pass219 {

struct RnaTranscriptionContext final {
    const InheritedBindings* inherited{nullptr};
    const Frame5184* source_frame{nullptr};
};

// ABI organization declaration only.
// No transcription execution authority in I1.
class RnaTranscription final {
public:
    RnaTranscription() = delete;

    [[nodiscard]]
    static MembraneReceipt admit(
        const RnaTranscriptionContext&
    ) noexcept;
};

}  // namespace hhs::pass219
