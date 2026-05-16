"""Small helper script used during development to exercise the extractor.

This file is a temporary runner that demonstrates how to instantiate
`UnitExtractor` with a small extractor mapping. It is not used by the
package itself; the changes here are limited to adding documentation and
comments for readability.
"""

from ai.ai_tools.unit_extractor.controllers import UnitExtractor
from ai.ai_tools.unit_extractor.extractors import TextExtractor


EXTRACTORS = {
    ".txt": TextExtractor(),
    ".h": TextExtractor(),
}


if __name__ == "__main__":
    # example data path used in local development
    test_path = r"C:\All University Materials\Project\ICT304-project\ai\ai_tools\data_extractor\data\raw\ICT283_contents"
    # run the extractor and collect results (function names mirror API)
    results = UnitExtractor(**EXTRACTORS).run(test_path)
    