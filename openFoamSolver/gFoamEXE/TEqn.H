{


    fvScalarMatrix TEqn
    (
        fvm::ddt(T)
      + fvm::div(phi, T)
      - fvm::laplacian(Db, T)


    );

    TEqn.relax();

    fvOptions.constrain(TEqn);

    fvOptions.correct(T);

    TEqn.solve();

}
