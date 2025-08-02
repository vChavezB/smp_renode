set(SB_CONF_FILE ${CMAKE_CURRENT_LIST_DIR}/sysbuild.conf)

find_package(Sysbuild REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(sysbuild LANGUAGES)