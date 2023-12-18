class Optimization_Step():
    """Each instantiation of this class corresponds to a step in the optimization process.

    Note
    ----
    The stored forces and the energy belong to "structure", not to "updated_structure".
    
    """
    def __init__(self, structure, forces, energy, updated_structure=None):
        """Initialize the optimization step.

        Parameters
        ----------
        structure: structure.Structure
            The initial structure of the optimization step
        forces: numpy.ndarray of shape (n_atoms_in_structure, 3)
            Forces acting on structure.atoms; [eV/AA]
        energy: number
            The energy of structure
        update_structure: structure.Structure
            The updated structure (generated by letting the forces act on structure)

        """
        self.structure = structure
        self.forces = forces
        self.energy = energy
        self.updated_structure = updated_structure

    def add_updated_structure(self, updated_structure):
        """Add/change the updated structure of the optimization step.

        Parameters
        ----------
        update_structure: structure.Structure
            The updated structure (generated by letting the forces act on structure)

        """
        self.updated_structure = updated_structure

    def remove_updated_structure(self):
        """Remove the updated structure from the optimization step.

        """
        self.updated_structure = None
