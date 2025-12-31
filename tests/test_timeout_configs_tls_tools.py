def test_timeout_configs_include_tls_tools() -> None:
    from utils.timeout import calculate_adaptive_timeout

    assert calculate_adaptive_timeout("tlsCycleAdaptation") == 300
    assert calculate_adaptive_timeout("tlsCoordinator") == 300


def test_tls_tool_timeout_grows_with_route_size() -> None:
    from utils.timeout import calculate_adaptive_timeout

    small = calculate_adaptive_timeout("tlsCycleAdaptation", {"route_files_bytes": 0})
    large = calculate_adaptive_timeout("tlsCycleAdaptation", {"route_files_bytes": 500_000})

    assert large > small
