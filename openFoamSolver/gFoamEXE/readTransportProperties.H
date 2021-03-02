singlePhaseTransportModel laminarTransport(U, phi);


dimensionedScalar Db("Db", pow(dimLength,2)/dimTime, laminarTransport);
//dimensionedScalar kb("kb", dimless/dimTime/dimTemperature, laminarTransport);
//dimensionedScalar kbr("kbr", dimless/dimTime, laminarTransport);
//dimensionedScalar ks("ks", dimless/dimTime, laminarTransport);

// Thermal expansion coefficient [1/K]
dimensionedScalar beta
(
    "beta",
    dimless/dimTemperature,
    laminarTransport
);

// Reference temperature [K]
dimensionedScalar TRef("TRef", dimTemperature, laminarTransport);

// Laminar Prandtl number
dimensionedScalar Pr("Pr", dimless, laminarTransport);

// Turbulent Prandtl number
dimensionedScalar Prt("Prt", dimless, laminarTransport);
