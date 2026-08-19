# C++ Style Guide Summary

## Modern C++ Standards
- Target modern C++ (C++17 / C++20).
- Use RAII (Resource Acquisition Is Initialization) for all resource management.
- Prefer `std::unique_ptr` and `std::shared_ptr` over raw pointers.
- Use `auto` when type is explicitly stated on the right-hand side or with complex iterators.
- Use `const` and `constexpr` wherever values or member functions do not mutate state.
- Prefer `std::string_view` and `std::span` for non-owning read access.
