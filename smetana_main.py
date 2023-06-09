#!/usr/bin/env python

import argparse
import textwrap

from reframed import set_default_solver
from interface import main

if __name__ == '__main__':

    print('In the main function')

    parser = argparse.ArgumentParser(description="Calculate SMETANA scores for one or multiple microbial communities.",
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('models', metavar='MODELS', nargs='+',
                        help=textwrap.dedent(
        """
        Multiple single-species models (one or more files).
        
        You can use wild-cards, for example: models/*.xml, and optionally protect with quotes to avoid automatic bash
        expansion (this will be faster for long lists): "models/*.xml". 
        """
        ))

    parser.add_argument('-c', '--communities', metavar='COMMUNITIES.TSV', dest='communities',
                        help=textwrap.dedent(
        """
        Run SMETANA for multiple (sub)communities.
        The communities must be specified in a two-column tab-separated file with community and organism identifiers.
        The organism identifiers should match the file names in the SBML files (without extension).
        
        Example:
            community1\torganism1
            community1\torganism2
            community2\torganism1
            community2\torganism3
            
        """
    ))

    parser.add_argument('-o', '--output', dest='output', help="Prefix for output file(s).")
    parser.add_argument('-s',dest='species', help="add names of models")
    parser.add_argument('--flavor', help="Expected SBML flavor of the input files (cobra or fbc2).")
    parser.add_argument('-m', '--media', dest='media', help="Run SMETANA for given media (comma-separated).")
    parser.add_argument('--mediadb', help="Media database file")

    oxygen = parser.add_mutually_exclusive_group()
    oxygen.add_argument('--aerobic', action='store_true', help="Simulate an aerobic environment.")
    oxygen.add_argument('--anaerobic', action='store_true', help="Simulate an anaerobic environment.")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('-g', '--global', dest='global', action='store_true', help="Run global analysis with MIP/MRO (faster).")
    mode.add_argument('-d', '--detailed',  dest='smetana', action='store_true', help="Run detailed SMETANA analysis (slower).")
    mode.add_argument('-a', '--abiotic',  dest='abiotic', help="Test abiotic perturbations with given list of compounds.")
    mode.add_argument('-ar', '--abiotic-rm',  dest='abiotic_rm', help="Test abiotic perturbations (removing compounds from media).")
    mode.add_argument('-b', '--biotic',  dest='biotic', help="Test biotic perturbations with given list of species.")

    parser.add_argument('-p', type=int, default=1, help="Number of components to perturb simultaneously (default: 1).")
    parser.add_argument('-n', type=int, default=1, help=textwrap.dedent(
        """
        Number of random perturbation experiments per community (default: 1).
        Selecting n = 0 will test all single species/compound perturbations exactly once.
        """
    ))

    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose', help="Switch to verbose mode")
    parser.add_argument('-z', '--zeros', action='store_true', dest='zeros', help="Include entries with zero score.")
    parser.add_argument('--solver', help="Change default solver (current options: 'gurobi', 'cplex').")
    parser.add_argument('--molweight', action='store_true', help="Use molecular weight minimization (recomended).")
    parser.add_argument('--lp', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--exclude', help="List of compounds to exclude from calculations (e.g.: inorganic compounds).")
    parser.add_argument('--debug', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--no-coupling', action='store_true', help="Don't compute species coupling scores.")

    args = parser.parse_args()

    if args.smetana:
        mode = "detailed"
        other = None
    elif args.abiotic:
        mode = "abiotic"
        other = args.abiotic
    elif args.abiotic_rm:
        mode = "abiotic-rm"
        other = args.abiotic_rm
    elif args.biotic:
        mode = "biotic"
        other = args.biotic
    else:
        mode = "global"
        other = None

    aerobic = None
    if args.aerobic:
        aerobic = True
    if args.anaerobic:
        aerobic = False

    if args.debug and mode != "global":
        parser.error('For the moment --debug is only available in global mode.')

    if args.solver:
        set_default_solver(args.solver)

    main(
        models=args.models,
        communities=args.communities,
        mode=mode,
        output=args.output,
        flavor=args.flavor,
        media=args.media,
        mediadb=args.mediadb,
        aerobic=aerobic,
        zeros=args.zeros,
        verbose=args.verbose,
        min_mol_weight=args.molweight,
        use_lp=args.lp,
        exclude=args.exclude,
        debug=args.debug,
        other=other,
        p=args.p,
        n=args.n,
        ignore_coupling=args.no_coupling,
    )
