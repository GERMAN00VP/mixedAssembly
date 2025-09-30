
from typing import List
import sys
from . import remove_frameshifts as rf
from . import build_priors as bp
from . import run_mixed_assembly as rma

def remove_frameshifts_cli(argv: List[str] = None) -> int:
    """Console entry for remove_frameshifts"""
    argv = argv if argv is not None else sys.argv[1:]
    return rf.main(argv)

def build_priors_cli(argv: List[str] = None) -> int:
    """Console entry for build_priors"""
    argv = argv if argv is not None else sys.argv[1:]
    return bp.main(argv)

def run_mixed_assembly_cli(argv: List[str] = None) -> int:
    """Console entry for run_mixed_assembly"""
    argv = argv if argv is not None else sys.argv[1:]
    return rma.main(argv)
