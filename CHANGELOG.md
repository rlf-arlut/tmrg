This file contains the updates of on the version.
It follows these [rules](https://keepachangelog.com/en/1.0.0/).
The script handling the release, uses it as parsing rules, so please maintain formatting.

The latest version (highest in this file) is the running version.
When updating it, keep in mind.
A [template](#[template]) is available at the end with the different sections.

## [0.1.0]
### Added
- Changelog
- Release script
- Limited support for SystemVerilog
- Verible in CI for SystemVerilog files
- Testcase for DFF with aynchronous reset when using SystemVerilog `always_ff` construct [Issue 50](https://gitlab.cern.ch/tmrg/tmrg/-/issues/50)
- Support for Verilog `param` construct in libraries
- [Issue 57](https://gitlab.cern.ch/tmrg/tmrg/-/issues/57): Support for Verilog attributes

### Changed
- Increased python recursion limit to 4000

### Fixed
- [Issue 26](https://gitlab.cern.ch/tmrg/tmrg/-/issues/26): improved testing for `casez`/`casex` construct
- [Issue 25](https://gitlab.cern.ch/tmrg/tmrg/-/issues/25): SystemVerilog labelled `endmodule` construct support
- [Issue 28](https://gitlab.cern.ch/tmrg/tmrg/-/issues/28): SystemVerilog `logic` construct support
- [Issue 29](https://gitlab.cern.ch/tmrg/tmrg/-/issues/29): SystemVerilog `always_ff` construct support
- [Issue 31](https://gitlab.cern.ch/tmrg/tmrg/-/issues/31): SystemVerilog `always_comb` construct support
- [Issue 32](https://gitlab.cern.ch/tmrg/tmrg/-/issues/32): SystemVerilog `always_latch` construct support
- [Issue 33](https://gitlab.cern.ch/tmrg/tmrg/-/issues/33): SystemVerilog `import <package>::<parameter>` construct support
- [Issue 27](https://gitlab.cern.ch/tmrg/tmrg/-/issues/27): SystemVerilog `unique case` construct support
- [Issue 36](https://gitlab.cern.ch/tmrg/tmrg/-/issues/36): SystemVerilog testing using Verible
- [Issue 34](https://gitlab.cern.ch/tmrg/tmrg/-/issues/34): SystemVerilog `for` construct support
- [Issue 38](https://gitlab.cern.ch/tmrg/tmrg/-/issues/38): SystemVerilog `'0` construct on right-hand side support
- [Issue 43](https://gitlab.cern.ch/tmrg/tmrg/-/issues/43): SystemVerilog `int'()` cast construct in `for`-loop support
- [Issue 40](https://gitlab.cern.ch/tmrg/tmrg/-/issues/40): SystemVerilog `size`-definition of unpacked array construct support
- [Issue 41](https://gitlab.cern.ch/tmrg/tmrg/-/issues/41): SystemVerilog unpacked array construct in ports declaration support
- [Issue 42](https://gitlab.cern.ch/tmrg/tmrg/-/issues/42): SystemVerilog unpacked array of packed arrays in port definition construct support
- [Issue 44](https://gitlab.cern.ch/tmrg/tmrg/-/issues/44): SystemVerilog voting of unpacked array of packed arrays construct support
- [Issue 45](https://gitlab.cern.ch/tmrg/tmrg/-/issues/45): SystemVerilog localparam construct support
- [Issue 48](https://gitlab.cern.ch/tmrg/tmrg/-/issues/48): SystemVerilog genvar in for-loop was not correctly triplicated
- [Issue 47](https://gitlab.cern.ch/tmrg/tmrg/-/issues/47): SystemVerilog package parameter in module IO width support
- [Issue 46](https://gitlab.cern.ch/tmrg/tmrg/-/issues/46): SystemVerilog right-hand side cast to certain number of bits construct support
- [Issue 49](https://gitlab.cern.ch/tmrg/tmrg/-/issues/49): SystemVerilog right-hand side cast to certain number of bits construct support
- [Issue 53](https://gitlab.cern.ch/tmrg/tmrg/-/issues/53): SystemVerilog unpacked array of packed array as `localparam` construct support
- [Issue 52](https://gitlab.cern.ch/tmrg/tmrg/-/issues/52): Improved reproducibility across different systems
- [Issue 58](https://gitlab.cern.ch/tmrg/tmrg/-/issues/58): Expressions in case items are not output correctly
- [Issue 59](https://gitlab.cern.ch/tmrg/tmrg/-/issues/59): Blocking procedural assingment

### Deprecated

### Removed


## [0.0.0]
### Added
Original version of tmrg before releases were introduced

## [Template]
### Added
- new features
### Changed
- changes in existing functionality
### Deprecated
- soon-to-be removed features
### Removed
- now removed features
### Fixed
- any bug fixes
### Security
- vulnerability addressed
