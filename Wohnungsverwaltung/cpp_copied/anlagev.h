#ifndef ANLAGEV_H
#define ANLAGEV_H

#include <FL/Fl_Group.H>
#include <FL/Fl_Output.H>

class FlatOutput : public Fl_Output {
    public:
        FlatOutput(int x, int y, int w);
        void draw();
};

class PageOne : public Fl_Group {
    public:
        PageOne(int x, int y, int w, int h);
    private:
        FlatOutput *_pName;
        FlatOutput *_pVorname;
        FlatOutput *_pSteuernr;
        FlatOutput *_lfdNr;
        FlatOutput *_pWhgStrasse;
        FlatOutput *_pWhgPlz;
        FlatOutput *_pWhgOrt;
        FlatOutput *_pEinhwert_Az;
        FlatOutput *_pNtzgFeWo;
        FlatOutput *_pWohnflaeche;
        FlatOutput *_pMieteNetto;
        FlatOutput *_pNK;
        FlatOutput *_pSummeEin;
        FlatOutput *_pSummeWK;
        FlatOutput *_pUeberschuss;
        FlatOutput *_pZurechng;

};

class PageTwo : public Fl_Group {
    public:
        PageTwo(int x, int y, int w, int h);
    private:
        FlatOutput *_pStnrNameEtc;
        FlatOutput *_pAfaLinear;
        FlatOutput *_pAfaDegr;
        FlatOutput *_pAfaProzent;
        FlatOutput *_pAfaWieVj;
        FlatOutput *_pAfaBetrag;
        FlatOutput *_pAufwandVollAbz;
        FlatOutput *_pAufwand5JVert;
        FlatOutput *_pAufwand5JAbzVj;
        FlatOutput *_pNkMieter; //Zeile 46
        FlatOutput *_pVerwaltKostenBez;
        FlatOutput *_pVerwaltKosten;
        FlatOutput *_pSonstKostenBez;
        FlatOutput *_pSonstKosten;
        FlatOutput *_pSummeWK;
};

class AnlageV : public Fl_Group {
    public:
        AnlageV(int x, int y, int w, int h);
        virtual ~AnlageV();
        void changePage();
        Fl_Group* getPage(int idx) const;

    protected:

    private:
        PageOne *_pPageOne;
        PageTwo *_pPageTwo;
        mutable Fl_Group *_pShownPage;
};

#endif // ANLAGEV_H
