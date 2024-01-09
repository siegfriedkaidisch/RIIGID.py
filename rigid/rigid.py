import pickle
import warnings

from ase.calculators.vasp.vasp import Vasp
from ase.io.trajectory import Trajectory

from rigid.convergence.cc_displacement import CC_Displacement
from rigid.library.misc import copy_docstring
from rigid.optimizer.GDWAS import GDWAS
from rigid.structure import Structure


class RIGID:
    """RIGID Geometry Optimization

    The structure under investigation is separated into so-called fragments, which are a
    set of atoms with fixed bonds between them, thus forming a rigid body. Using an ASE
    calculator (e.g. VASP), the forces on each atom are found, which are then used to
    calculate the force and torque on each fragment. Just like rigid bodies, the fragments
    are then moved in accordance to these forces and torques (like rigid bodies). This way,
    the energy of this system of (rigid) fragments is minimized.

    The user has to provide the structure, define the fragments and choose calculator,
    optimizer and convergence criterion.

    Attributes
    ----------
    start_structure : ase.atoms.Atoms
        The atoms forming the structure to be optimized.
        This is an ase.Atoms object and should include the
        correct unit cell (for periodic systems).
    name : str
        The name of the studied system.
    calculator : ase.calculators.calculator.Calculator
        The used ASE calculator object
    optimizer : optimizer.Optimizer
        The used optimizer object
    convergence_criterion : convergence_criterion.Convergence_Criterion
        The used convergence criterion object

    """

    def __init__(self, atoms, name):
        """Initialize a RIGID geometry optimization.

        Parameters
        ----------
        atoms : ase.atoms.Atoms
            The atoms forming the structure to be optimized.
            This is an ase.Atoms object and should include the
            correct unit cell (for periodic systems).
        name : str
            The name of the studied system. E.g.: "Benzene"

        """
        self.start_structure = Structure(atoms=atoms)
        self.name = name
        print("+~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+")
        print("RIGID geometry optimization of: ", self.name)
        print("+~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~+")

    @copy_docstring(Structure.define_fragment_by_indices)
    def define_fragment_by_indices(self, *args, **kwargs):
        self.start_structure.define_fragment_by_indices(*args, **kwargs)
        print("New fragment defined using indices.")

    def set_calculator(self, calculator, settings={}):
        """Set the ASE Calculator to be used for optimizing the structure.

        Parameters
        ----------
        calculator: ase.calculators.calculator.Calculator or str
            The user can provide an ASE Calculator object or the name (string) of
            the calculator that shall be used.
        settings: dict, default:{}
            If the calculator is defined using a string (see above), calculator settings
            can be defined using this parameter. If an ASE calculator is provided, this
            dictionary is ignored, the calculator is assumed to be already set up!

        Raises
        ------
        Exception
            If the provided calculator name (string) is not known.

        """
        if isinstance(calculator, str):
            if settings == {}:
                warnings.warn(
                    "Warning: No calculator settings provided! Depending on the calculator, the calculation may fail."
                )

            if calculator.lower() == "vasp":
                calculator = Vasp(**settings)
            else:
                raise Exception(
                    "Calculator not known... did you write the name correctly? Tip: Maybe initialize the calculator in your code and hand it to RIGID, instead of handing its name (string) to RIGID."
                )

        self.calculator = calculator
        print("Calculator set to: ", str(type(self.calculator)))
        print("Calculator Settings:")
        if self.calculator.parameters == {}:
            print("   -")
        for entry in self.calculator.parameters:
            print("   - " + str(entry) + ": " + str(self.calculator.parameters[entry]))

    def set_optimizer(self, optimizer, settings={}):
        """Set the optimizer to be used for optimizing the structure.

        Parameters
        ----------
        optimizer : optimizer.Optimizer or str
            The user can provide an Optimizer object or the name (string) of
            the optimizer that shall be used.
        settings: dict, default:{}
            If the optimizer is defined using a string (see above), optimizer settings
            can be defined using this parameter. If an Optimizer object is provided, this
            dictionary is ignored, the optimizer is assumed to be already set up!

        Raises
        ------
        Exception
            If the provided optimizer name (string) is not known.

        """
        if isinstance(optimizer, str):
            provided_optimizer_was_string = True
            if settings == {}:
                warnings.warn(
                    "Warning: No optimizer settings provided! Using default settings."
                )

            if optimizer.lower() == "gdwas":
                optimizer = GDWAS(**settings)
            else:
                raise Exception(
                    "Optimizer not known... did you write the name correctly? Tip: Maybe initialize the optimizer in your code and hand it to RIGID, instead of handing its name (string) to RIGID."
                )
        else:
            provided_optimizer_was_string = False

        self.optimizer = optimizer
        print("Optimizer set to: ", str(type(self.optimizer)))
        print("Optimizer Settings:")
        if provided_optimizer_was_string:
            if settings == {}:
                print("   - No settings provided!")
            for entry in settings:
                print("   - " + str(entry) + ": " + str(settings[entry]))
        else:
            print(
                "   - Unknown, because an initialized optimizer was provided to RIGID."
            )

    def set_convergence_criterion(self, convergence_criterion, settings={}):
        """Set the convergence criterion for optimizing the structure.

        Parameters
        ----------
        convergence_criterion : convergence_criterion.Convergence_Criterion or str
            The user can provide a convergence criterion object or the name (string) of
            the convergence criterion that shall be used.
        settings: dict, default:{}
            If the convergence criterion is defined using a string (see above), convergence criterion settings
            can be defined using this parameter. If a convergence criterion object is provided, this
            dictionary is ignored, the convergence criterion is assumed to be already set up!

        Raises
        ------
        Exception
            If the provided convergence criterion name (string) is not known.

        """
        if isinstance(convergence_criterion, str):
            provided_convergence_criterion_was_string = True
            if settings == {}:
                warnings.warn(
                    "Warning: No convergence criterion settings provided! Using default settings."
                )

            if convergence_criterion.lower() == "cc_displacement":
                convergence_criterion = CC_Displacement(**settings)
            else:
                raise Exception(
                    "Convergence criterion not known... did you write the name correctly? Tip: Maybe initialize the convergence criterion in your code and hand it to RIGID, instead of handing its name (string) to RIGID."
                )
        else:
            provided_convergence_criterion_was_string

        self.convergence_criterion = convergence_criterion
        print("Convergence criterion set to: ", str(type(self.convergence_criterion)))
        print("Convergence criterion Settings:")
        if provided_convergence_criterion_was_string:
            if settings == {}:
                print("   - No settings provided!")
            for entry in settings:
                print("   - " + str(entry) + ": " + str(settings[entry]))
        else:
            print(
                "   - Unknown, because an initialized convergence criterion was provided to RIGID."
            )

    def run(self):
        """Run the optimization"""
        # Perform rigid optimization
        self.optimizer.run(
            start_structure=self.start_structure,
            calculator=self.calculator,
            convergence_criterion=self.convergence_criterion,
        )

        # Save some results
        self.save_optimization_history()
        self.create_trajectory_file_from_optimization_history()

        # Print some results
        self.print_optimization_summary()

    def save_optimization_history(self):
        """Save the optimization history (list of optimization steps) as a pickle file."""
        optimization_history = self.optimizer.optimization_history
        fn = self.name + ".pk"
        f = open(fn, "wb")
        pickle.dump(optimization_history, f)
        f.close()
        print("Optimization history saved as pickle file: ", fn)

    def create_trajectory_file_from_optimization_history(self):
        """Creates and saves the trajectory file of the optimization."""
        optimization_history = self.optimizer.optimization_history
        fn = self.name + ".traj"
        traj = Trajectory(fn, "w")
        for optimization_step in optimization_history:
            traj.write(optimization_step.structure.atoms)
        traj.close()
        print("Optimization trajectory saved as ", fn)

    def print_optimization_summary(self):
        """Print Information about the Optimization."""
        print("Summary of Optimization:")
        optimization_history = self.optimizer.optimization_history
        for iteration, step in enumerate(optimization_history):
            print("Optimization Step " + str(iteration) + ":")
            print("   Energy [eV]: " + str(step.energy))