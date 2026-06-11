import numpy as np


def naca_4digit(m=0.02, p=0.4, t=0.12, n=241, chord=1.0):
    """
    Generate closed NACA 4-digit airfoil coordinates.

    m = maximum camber as fraction of chord
    p = location of maximum camber as fraction of chord
    t = maximum thickness as fraction of chord

    For NACA 2412:
        m = 0.02
        p = 0.4
        t = 0.12

    Coordinate order:
        trailing edge upper -> leading edge -> trailing edge lower
    """

    beta = np.linspace(0.0, np.pi, n)
    x = 0.5 * (1.0 - np.cos(beta))  # cosine spacing, LE to TE

    yt = 5.0 * t * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1015 * x**4
    )

    yc = np.zeros_like(x)
    dyc_dx = np.zeros_like(x)

    for i, xi in enumerate(x):
        if xi < p:
            yc[i] = m / p**2 * (2.0 * p * xi - xi**2)
            dyc_dx[i] = 2.0 * m / p**2 * (p - xi)
        else:
            yc[i] = m / (1.0 - p)**2 * ((1.0 - 2.0 * p) + 2.0 * p * xi - xi**2)
            dyc_dx[i] = 2.0 * m / (1.0 - p)**2 * (p - xi)

    theta = np.arctan(dyc_dx)

    xu = x - yt * np.sin(theta)
    zu = yc + yt * np.cos(theta)

    xl = x + yt * np.sin(theta)
    zl = yc - yt * np.cos(theta)

    # Upper surface: TE -> LE
    x_upper = xu[::-1]
    z_upper = zu[::-1]

    # Lower surface: LE -> TE
    x_lower = xl[1:]
    z_lower = zl[1:]

    x_closed = np.concatenate([x_upper, x_lower])
    z_closed = np.concatenate([z_upper, z_lower])

    return chord * x_closed, chord * z_closed


def triangle_normal(p1, p2, p3):
    v1 = p2 - p1
    v2 = p3 - p1
    normal = np.cross(v1, v2)
    norm = np.linalg.norm(normal)

    if norm == 0.0:
        return np.array([0.0, 0.0, 0.0])

    return normal / norm


def write_ascii_stl(filename, triangles, solid_name="naca2412Wing"):
    with open(filename, "w") as f:
        f.write(f"solid {solid_name}\n")

        for tri in triangles:
            p1, p2, p3 = tri
            n = triangle_normal(p1, p2, p3)

            f.write(f"  facet normal {n[0]:.8e} {n[1]:.8e} {n[2]:.8e}\n")
            f.write("    outer loop\n")
            f.write(f"      vertex {p1[0]:.8e} {p1[1]:.8e} {p1[2]:.8e}\n")
            f.write(f"      vertex {p2[0]:.8e} {p2[1]:.8e} {p2[2]:.8e}\n")
            f.write(f"      vertex {p3[0]:.8e} {p3[1]:.8e} {p3[2]:.8e}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")

        f.write(f"endsolid {solid_name}\n")


def generate_rectangular_wing(
    chord=1.0,
    span=5.0,
    m=0.02,
    p=0.4,
    thickness=0.12,
    n_airfoil=241,
    n_span=81,
    filename="wing_NACA2412_zeroSweep.stl"
):
    """
    Generate full rectangular finite wing STL using a cambered NACA 4-digit airfoil.

    Coordinate system:
        x = chord / freestream direction
        y = span direction
        z = vertical / airfoil thickness direction

    Geometry:
        sweep = 0 deg
        twist = 0 deg
        dihedral = 0 deg
        geometric AoA = 0 deg
    """

    x_airfoil, z_airfoil = naca_4digit(
        m=m,
        p=p,
        t=thickness,
        n=n_airfoil,
        chord=chord
    )

    n_profile = len(x_airfoil)

    y_stations = np.linspace(-span / 2.0, span / 2.0, n_span)

    vertices = []

    for y in y_stations:
        section = []
        for x, z in zip(x_airfoil, z_airfoil):
            section.append(np.array([x, y, z]))
        vertices.append(section)

    triangles = []

    # Main wing surface
    for i in range(n_span - 1):
        for j in range(n_profile):
            j_next = (j + 1) % n_profile

            p1 = vertices[i][j]
            p2 = vertices[i + 1][j]
            p3 = vertices[i + 1][j_next]
            p4 = vertices[i][j_next]

            triangles.append([p1, p2, p3])
            triangles.append([p1, p3, p4])

    # Left tip cap
    left_center = np.mean(vertices[0], axis=0)

    for j in range(n_profile):
        j_next = (j + 1) % n_profile

        p1 = left_center
        p2 = vertices[0][j_next]
        p3 = vertices[0][j]

        triangles.append([p1, p2, p3])

    # Right tip cap
    right_center = np.mean(vertices[-1], axis=0)

    for j in range(n_profile):
        j_next = (j + 1) % n_profile

        p1 = right_center
        p2 = vertices[-1][j]
        p3 = vertices[-1][j_next]

        triangles.append([p1, p2, p3])

    write_ascii_stl(filename, triangles, solid_name="NACA2412_rectangularWing")

    print(f"STL written      : {filename}")
    print(f"Airfoil          : NACA 2412")
    print(f"Chord            : {chord} m")
    print(f"Span             : {span} m")
    print(f"Aspect ratio     : {span**2 / (span * chord):.2f}")
    print(f"Reference area   : {span * chord:.3f} m^2")
    print(f"Max camber       : {m * 100:.1f}% chord")
    print(f"Camber location  : {p * 100:.1f}% chord")
    print(f"Thickness        : {thickness * 100:.1f}% chord")
    print(f"Airfoil points   : {n_profile}")
    print(f"Span stations    : {n_span}")
    print(f"Triangles        : {len(triangles)}")


if __name__ == "__main__":
    generate_rectangular_wing(
        chord=1.0,
        span=5.0,
        m=0.02,
        p=0.4,
        thickness=0.12,
        n_airfoil=241,
        n_span=81,
        filename="wing_NACA2412_zeroSweep.stl"
    )
