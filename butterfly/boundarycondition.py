# coding=utf-8
"""Collection of OpenFOAM boundary conditions (e.g. wall, inlet, outlet)."""
from copy import deepcopy
from collections import OrderedDict
from fields import AtmBoundaryLayerInletVelocity, AtmBoundaryLayerInletK, \
    AtmBoundaryLayerInletEpsilon, Calculated, EpsilonWallFunction, FixedValue, \
    InletOutlet, KqRWallFunction, NutkWallFunction, NutkAtmRoughWallFunction, \
    Slip, ZeroGradient, AlphatJayatillekeWallFunction, FixedFluxPressure, Empty, \
    Field


class BoundaryCondition(object):
    """Boundary condition base class.

    Attributes:
        bcType: Boundary condition type. e.g.(patch, wall)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for temperature in Kelvin (300)
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    # TODO(Mostapha): Write a descriptor for field and replace all properties
    def __init__(self, bcType='patch', refLevels=None, T=None, U=None, p=None,
                 k=None, epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        self.type = bcType
        self.refLevels = (1, 1) if not refLevels else tuple(int(v) for v in refLevels)
        # set default values
        self.T = T
        self.U = U
        self.p = p
        self.k = k
        self.epsilon = epsilon
        self.nut = nut
        self.alphat = alphat
        self.p_rgh = p_rgh

    @property
    def T(self):
        "T boundary condition."
        return self._T

    @T.setter
    def T(self, t):
        self._T = self.tryGetField(t or ZeroGradient())

    @property
    def U(self):
        "U boundary condition."
        return self._U

    @U.setter
    def U(self, u):
        self._U = self.tryGetField(u or ZeroGradient())

    @property
    def p(self):
        "p boundary condition."
        return self._p

    @p.setter
    def p(self, p):
        self._p = self.tryGetField(p or ZeroGradient())

    @property
    def k(self):
        "k boundary condition."
        return self._k

    @k.setter
    def k(self, k_):
        self._k = self.tryGetField(k_ or ZeroGradient())

    @property
    def epsilon(self):
        "epsilon boundary condition."
        return self._epsilon

    @epsilon.setter
    def epsilon(self, e):
        self._epsilon = self.tryGetField(e or ZeroGradient())

    @property
    def nut(self):
        "nut boundary condition."
        return self._nut

    @nut.setter
    def nut(self, n):
        self._nut = self.tryGetField(n or ZeroGradient())

    @property
    def alphat(self):
        "alphat boundary condition."
        return self._alphat

    @alphat.setter
    def alphat(self, a):
        self._alphat = self.tryGetField(a or ZeroGradient())

    @property
    def p_rgh(self):
        "p_rgh boundary condition."
        return self._p_rgh

    @p_rgh.setter
    def p_rgh(self, prgh):
        self._p_rgh = self.tryGetField(prgh or ZeroGradient())

    def isBoundaryCondition(self):
        """Return True for boundary conditions."""
        return True

    @staticmethod
    def tryGetField(f):
        """Try getting the field from the input.

        The method will return the input if it is an instance of class <Field>,
        otherwise it tries to create the field from a dictionary and finally
        tries to create it from the string.
        """
        if isinstance(f, Field):
            return f
        elif isinstance(f, (dict, OrderedDict)):
            return Field.fromDict(f)
        else:
            try:
                return Field.fromString(f)
            except Exception:
                raise ValueError(
                    'Failed to create an OpenFOAM field from {}. Use a valid value.'
                    .format(f))

    def duplicate(self):
        """Duplicate Boundary Condition."""
        return deepcopy(self)

    def ToString(self):
        """Overwrite .NET ToString."""
        return self.__repr__()

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}; refLevels {}".format(self.__class__.__name__,
                                             self.type, self.refLevels)


class BoundingBoxBoundaryCondition(BoundaryCondition):
    """Bounding box boundary condition for bounding box geometry.

    It returns a boundary condition of ZeroGradient for all the inputs.
    """

    def __init__(self, refLevels=None):
        """Init bounday condition."""
        U = ZeroGradient()
        p = ZeroGradient()
        k = ZeroGradient()
        epsilon = ZeroGradient()
        nut = ZeroGradient()
        refLevels = None
        T = ZeroGradient()
        alphat = ZeroGradient()
        p_rgh = ZeroGradient()
        super(BoundingBoxBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut, alphat, p_rgh
        )


class EmptyBoundaryCondition(BoundaryCondition):
    """Empty boundary condition.

    It returns a boundary condition of Empty for all the inputs.
    """

    def __init__(self, refLevels=None):
        """Init bounday condition."""
        U = Empty()
        p = Empty()
        k = Empty()
        epsilon = Empty()
        nut = Empty()
        refLevels = None
        T = Empty()
        alphat = Empty()
        p_rgh = Empty()
        super(EmptyBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut, alphat, p_rgh
        )


class IndoorWallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition base class.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None, U=None, p=None, k=None,
                 epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or KqRWallFunction('0.1')
        epsilon = epsilon or EpsilonWallFunction(0.01)
        nut = nut or NutkWallFunction(0.01)
        T = T or ZeroGradient()
        alphat = alphat or AlphatJayatillekeWallFunction(
            value='0', isUniform=True, Prt='0.85')

        p_rgh = p_rgh or FixedFluxPressure(value='0', isUniform=True, rho='rhok')

        BoundaryCondition.__init__(self, 'wall', refLevels, T, U, p,
                                   k, epsilon, nut, alphat, p_rgh)


class FixedInletBoundaryCondition(BoundaryCondition):
    """Inlet boundary condition base class.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: Air velocity as fixed value (x, y, z).
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None, U=None, p=None, k=None,
                 epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or FixedValue('0.1')
        epsilon = epsilon or FixedValue('0.01')
        nut = Calculated('0')
        T = T if T else None
        alphat = ZeroGradient()
        p_rgh = ZeroGradient()

        BoundaryCondition.__init__(self, 'patch', refLevels, T, U, p,
                                   k, epsilon, nut, alphat, p_rgh)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.U, self.refLevels)


class FixedOutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition base class.

    Attributes:
        pressure: Pressure as a float (default: 0)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None, U=None, p=None, k=None,
                 epsilon=None, nut=None, alphat=None, p_rgh=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or ZeroGradient()
        p = p or FixedValue('0')
        k = k or ZeroGradient()
        epsilon = epsilon or ZeroGradient()
        nut = Calculated('0')
        T = T or ZeroGradient()
        alphat = ZeroGradient()
        p_rgh = ZeroGradient()

        super(FixedOutletBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut, alphat, p_rgh
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.p, self.refLevels)


class WindTunnelWallBoundaryCondition(BoundaryCondition):
    """Wall boundary condition for wall geometrys inside wind tunnel.

    Attributes:
        T: Optional input for Temperature.
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or KqRWallFunction('$internalField', isUnifrom=False)
        epsilon = epsilon or EpsilonWallFunction('$internalField', isUnifrom=False)
        nut = nut or NutkWallFunction('0.0')
        T = T or ZeroGradient()
        super(WindTunnelWallBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut
        )


class WindTunnelGroundBoundaryCondition(BoundaryCondition):
    """Wind tunnel ground boundary condition.

    Attributes:
        T: Optional input for Temperature.
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, ablConditions, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None):
        """Init bounday condition."""
        U = U or FixedValue('(0 0 0)')
        p = p or ZeroGradient()
        k = k or ZeroGradient()
        epsilon = epsilon or ZeroGradient()
        nut = NutkAtmRoughWallFunction.fromABLConditions(ablConditions,
                                                         'uniform 0')
        T = T or ZeroGradient()

        super(WindTunnelGroundBoundaryCondition, self).__init__(
            'wall', refLevels, T, U, p, k, epsilon, nut
        )


class WindTunnelInletBoundaryCondition(BoundaryCondition):
    """Wind tunnel atmBoundaryLayerInletVelocity boundary condition.

    Attributes:
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, ablConditions, refLevels=None, T=None, p=None,
                 nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = AtmBoundaryLayerInletVelocity.fromABLConditions(ablConditions)
        k = AtmBoundaryLayerInletK.fromABLConditions(ablConditions)
        epsilon = AtmBoundaryLayerInletEpsilon.fromABLConditions(ablConditions)
        p = p or ZeroGradient()
        nut = nut or Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelInletBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut)

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nvelocity {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.U.Uref, self.refLevels)


class WindTunnelOutletBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for wind tunnel.

    Attributes:
        pressure: Pressure as a float (default: 0)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or InletOutlet('uniform (0 0 0)', '$internalField')
        p = p or FixedValue('$pressure')
        k = k or InletOutlet('uniform $turbulentKE', '$internalField')
        epsilon = epsilon or InletOutlet('uniform $turbulentEpsilon', '$internalField')
        nut = nut or Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelOutletBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\npressure {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.p, self.refLevels)


class WindTunnelTopAndSidesBoundaryCondition(BoundaryCondition):
    """Outlet boundary condition for top and sides of wind tunnel.

    Attributes:
        pressure: Pressure as a float (default: 0)
        refLevels: A tuple for min, max refinment levels for this geometry.
        T: Optional input for Temperature.
        U: OpenFOAM value for U.
        p: OpenFOAM value for p.
        k: OpenFOAM value for k.
        epsilon: OpenFOAM value for epsilon.
        nut: OpenFOAM value for nut.
    """

    def __init__(self, refLevels=None, T=None,
                 U=None, p=None, k=None, epsilon=None, nut=None):
        """Init bounday condition."""
        # set default values for an inlet
        U = U or Slip()
        p = p or Slip()
        k = k or Slip()
        epsilon = epsilon or Slip()
        nut = Calculated('0')
        T = T or ZeroGradient()

        super(WindTunnelTopAndSidesBoundaryCondition, self).__init__(
            'patch', refLevels, T, U, p, k, epsilon, nut
        )

    def __repr__(self):
        """Bounday condition representatoin."""
        return "{}: {}\nrefLevels {}".format(
            self.__class__.__name__, self.type, self.refLevels)


if __name__ == '__main__':
    from conditions import ABLConditions
    abc = ABLConditions()
    print(WindTunnelWallBoundaryCondition())
    print(WindTunnelInletBoundaryCondition(abc))
    print(WindTunnelGroundBoundaryCondition(abc))
