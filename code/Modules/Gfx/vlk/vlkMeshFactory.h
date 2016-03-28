#pragma once
//------------------------------------------------------------------------------
/**
    @class Oryol::_priv::vlkMeshFactory
    @ingroup _priv
    @brief Vulkan implementation of meshFactory
*/
#include "Resource/ResourceState.h"
#include "Gfx/Core/gfxPointers.h"
#include "Gfx/Core/Enums.h"

namespace Oryol {
namespace _priv {

class mesh;

class vlkMeshFactory {
public:
    /// destructor
    ~vlkMeshFactory();

    /// setup with a pointer to the state wrapper object
    void Setup(const gfxPointers& ptrs);
    /// discard the factory
    void Discard();
    /// return true if the object has been setup
    bool IsValid() const;

    /// setup resource
    ResourceState::Code SetupResource(mesh& mesh);
    /// setup with 'raw' data
    ResourceState::Code SetupResource(mesh& mesh, const void* data, int32 size);
    /// discard the resource
    void DestroyResource(mesh& mesh);

    /// helper method to setup a mesh object as fullscreen quad
    ResourceState::Code createFullscreenQuad(mesh& mesh);
    /// create vertex and index buffers, all 
    ResourceState::Code create(mesh& mesh, const void* data, int32 size);

private:
    /// helper method to setup mesh vertex/index buffer attributes struct
    void setupAttrs(mesh& mesh);
    /// helper method to setup mesh primitive group array
    void setupPrimGroups(mesh& mesh);
    /// helper method to create d3d12 buffer objects for different usage scenarios
    void createBuffers(mesh& msh, int type, Usage::Code usage, const void* data, int32 size);

    gfxPointers pointers;
    bool isValid = false;
};

} // namespace _priv
} // namespace Oryol
