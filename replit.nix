{ pkgs }: {
    deps = [
        pkgs.python3
        pkgs.python3Packages.pip
        pkgs.python3Packages.virtualenv
        pkgs.python3Packages.streamlit
        pkgs.python3Packages.pandas
        pkgs.python3Packages.numpy
        pkgs.python3Packages.ifcopenshell
        pkgs.python3Packages.matplotlib
        pkgs.python3Packages.plotly
        pkgs.python3Packages.openpyxl
        pkgs.python3Packages.scipy
    ];
}
