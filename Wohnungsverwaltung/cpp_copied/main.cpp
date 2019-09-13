#include <FL/Fl.H>
#include <FL/Fl_Double_Window.H>
#include "anlagev.h"
#include <FL/Fl_Group.H>
#include <FL/Fl_Output.H>
#include <FL/Fl_Input.H>
#include <FL/Fl_Button.H>
#include <FL/Fl_Printer.H>
#include <FL/fl_draw.H>

/*
Fl_Printer allows to use all drawing, color, text, image, and clip FLTK functions, and to have them operate
 on printed page(s). There are two main, non exclusive, ways to use it.
 <ul><li>Print any widget (standard, custom, Fl_Window, Fl_Gl_Window) as it appears
 on screen, with optional translation, scaling and rotation. This is done by calling print_widget(),
 print_window() or print_window_part().
 <li>Use a series of FLTK graphics commands (e.g., font, text, lines, colors, clip, image) to
 compose a page appropriately shaped for printing.
 </ul>
 In both cases, begin by start_job(), start_page(), printable_rect() and origin() calls
 and finish by end_page() and end_job() calls.
 <p>Example of use: print a widget centered in a page
 \code
 #include <FL/Fl_Printer.H>
 #include <FL/fl_draw.H>
 int width, height;
 Fl_Widget *widget = ...  // a widget we want printed
 Fl_Printer *printer = new Fl_Printer();
 if (printer->start_job(1) == 0) {
  printer->start_page();
  printer->printable_rect(&width, &height);
  fl_color(FL_BLACK);
  fl_line_style(FL_SOLID, 2);
  fl_rect(0, 0, width, height);
  fl_font(FL_COURIER, 12);
  time_t now; time(&now); fl_draw(ctime(&now), 0, fl_height());
  printer->origin(width/2, height/2);
  printer->print_widget(widget, -widget->w()/2, -widget->h()/2);
  printer->end_page();
  printer->end_job();
 }
 delete printer;

 Unless it has been previously changed, the default paper size is A4.
 To change that, press the "Properties" button of the "Print" dialog window
 opened by an Fl_Printer::start_job() call. This opens a "Printer Properties" window where it's
 possible to select the adequate paper size. Finally press the "Save" button therein to assign
 the chosen paper size to the chosen printer for this and all further print operations.
 <br>Class Fl_RGB_Image prints but loses its transparency if it has one.
 See class Fl_PostScript_Graphics_Driver for a description of how UTF-8 strings appear in print.
 Use the static public attributes of this class to set the print dialog to other languages
 than English. For example, the "Printer:" dialog item Fl_Printer::dialog_printer can be set to French with:
 \code
 Fl_Printer::dialog_printer = "Imprimante:";
 \endcode
 before creation of the Fl_Printer object.
*/
AnlageV *pAnl;

void printAnlageV( Fl_Widget *pW, void *v) {
    int width, height;
    Fl_Printer *printer = new Fl_Printer();
    if ( printer->start_job( 2 ) == 0 ) {
        printer->start_page();
        printer->printable_rect( &width, &height );
        fl_color( FL_BLACK );
        //fl_line_style( FL_SOLID, 1 );
        //&fl_rect( 0, 0, width, height );
        //fl_font( FL_HELVETICA, 8 );

        printer->origin( width/2, height/2 );
        Fl_Group *widget = pAnl->getPage(1);
        printer->print_widget( widget, -widget->w()/2, -widget->h()/2 );
        printer->end_page();

        printer->start_page();
        printer->printable_rect( &width, &height );
        printer->origin( width/2, height/2 );
        widget = pAnl->getPage(2);
        printer->print_widget( widget, -widget->w()/2, -widget->h()/2 );
        printer->end_page();

        printer->end_job();
    }
    delete printer;
}


void changePage(Fl_Widget *pW, void *) {
    pAnl->changePage();
}

///////////////////////  EXAMPLE  ///////////////////////

class Form : public Fl_Group {
    public:
        Form():
        Fl_Group(0, 0, 600, 900)
        {
            begin();
                _pPageOne = new Fl_Group(0, 0, 500, 800);
                _pPageOne->begin();
                    Fl_Output *pOut1 = new Fl_Output( 200, 200, 100, 30);
                    pOut1->box(FL_FLAT_BOX);
                    pOut1->textsize(16);
                    pOut1->value("Page ONE");
                _pPageOne->end();

                _pPageTwo = new Fl_Group(0, 0, 500, 800);
                _pPageTwo->begin();
                    Fl_Output *pOut2 = new Fl_Output( 200, 200, 100, 30);
                    pOut2->box(FL_FLAT_BOX);
                    pOut2->textsize(16);
                    pOut2->value("Page TWO");
                _pPageTwo->end();
                _pPageTwo->hide();

            end();
            _pages[0] = _pPageOne;
            _pages[1] = _pPageTwo;
            _current = 0;
        }

        Fl_Group* getPage(int page) {
            if(page != _current) {
                switchPage();
            }
            return _pages[page];
        }

        void switchPage() {
            _pages[_current]->hide();
            _current = _current == 0 ? 1 : 0;
            _pages[_current]->set_visible();
        }

    private:
        Fl_Group *_pPageOne;
        Fl_Group *_pPageTwo;
        int _current;
        Fl_Group *_pages[2];
};

Form *pForm;

void printForm(Fl_Widget*, void*) {
    int width, height;
    Fl_Printer *printer = new Fl_Printer();
    if ( printer->start_job( 2 ) == 0 ) {
        printer->start_page();
        printer->printable_rect( &width, &height );
        fl_color( FL_BLACK );

        printer->origin( width/2, height/2 );
        Fl_Group *widget = pForm->getPage(0);
        printer->print_widget( widget, -widget->w()/2, -widget->h()/2 );
        printer->end_page();

        printer->start_page();
        printer->printable_rect( &width, &height );
        printer->origin( width/2, height/2 );
        widget = pForm->getPage(1);
        printer->print_widget( widget, -widget->w()/2, -widget->h()/2 );
        printer->end_page();

        printer->end_job();
    }
    delete printer;
}

void switchPage(Fl_Widget *pW, void *) {
    pForm->switchPage();
}

int main_() {
    Fl_Double_Window *pWin = new Fl_Double_Window(0, 0, 500, 800, "FLTK window");
    Fl_Button *pBtn = new Fl_Button(0, 20, 80, 25, "Print");
    pBtn->callback(printForm);
    Fl_Button *pBtn2 = new Fl_Button(0, 45, 80, 25, "Page");
    pBtn2->callback(switchPage);

    pForm = new Form();

    pWin->end();

    pWin->show();
    return Fl::run();
}

///////////////////////////////////////////////////////////////

int main(int argc, char **argv) {
    Fl_Double_Window *pWin = new Fl_Double_Window(0, 0, 624, 975, "FLTK window");
    fl_font( FL_HELVETICA, 8 );
    pWin->align(FL_ALIGN_CLIP|FL_ALIGN_INSIDE);
    pWin->begin();

    Fl_Button *pBtn = new Fl_Button(0, 20, 80, 25, "Print");
    pBtn->callback(printAnlageV);
    Fl_Button *pBtn2 = new Fl_Button(0, 45, 80, 25, "Page");
    pBtn2->callback(changePage);
    pAnl = new AnlageV(0, 0, 624, 975);

    pWin->end();

    pWin->show(argc, argv);
    return Fl::run();
}
