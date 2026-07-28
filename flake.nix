{
  description = "lastfm_pg - Last.fm playlist generator";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        pythonPackages = python.pkgs;
        pythonEnv = python.withPackages (ps: with ps; [
          pylast mastodon-py
        ]);
      in
      {
        packages.default = pythonPackages.buildPythonPackage {
          pname = "lastfm_pg";
          version = "0.1";
          pyproject = true;
          src = ./.;
          nativeBuildInputs = [ pythonPackages.hatchling ];
          propagatedBuildInputs = with pythonPackages; [ pylast mastodon-py ];
        };

        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv pythonPackages.ruff pythonPackages.pytest pythonPackages.pytest-cov ];
        };
      });
}
