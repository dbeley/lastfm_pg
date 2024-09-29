with import <nixpkgs> { };

let
  pythonPackages = python3Packages;
in pkgs.mkShell {
  buildInputs = [
    pythonPackages.python

    pythonPackages.pytest
    pythonPackages.black
    pythonPackages.pylast
    pythonPackages.mastodon-py
  ];

}
