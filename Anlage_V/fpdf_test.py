from fpdf import FPDF
import os

pdf = FPDF( 'P', 'mm', 'A4' )
pdf.add_page()
pdf.set_font('Arial', '', 14)
#pdf.set_left_margin( 15.0 )
#pdf.cell( 80, 10, "Kästchen mit Rand", border=1 ) #Kästchen hat 18mm Abstand zum linken Rand
#pdf.set_xy( 0.0, 0.0 ) # beim Druck: Abstand Basislinie oberer Blattrand: 18mm; Abstand vom linken Blattrand 10mm
#pdf.set_xy( 20.0, 30.0 ) # beim Druck: Abstand Basislinie oberer Blattrand: 45mm; Abstand vom linken Blattrand 28mm
# pdf.set_xy( 60.0, 80.0 ) # beim Druck: Abstand Basislinie oberer Blattrand: 72mm; Abstand vom linken Blattrand 47mm
# pdf.cell(40, 10, 'Hello World!' )
# pdf.set_xy( 0, 60 )
# pdf.cell( 80, 10, "Ich bin die zweite Zeile.", border=1 )
# pdf.set_xy( 10, 20 )
# pdf.cell( 80, 10, "Ich bin die dritte Zeile." )

for x, y, n in zip( range( 0, 10, 2 ), range( 0, 50, 10), range(5) ):
    pdf.set_xy( 10 + x,  10 + y )
    s = "I am line " + str(n+1) + ". x=%d, y=%d" % (10+x, 10+y)
    pdf.cell( 60, 6, s, border=0 )
    pdf.cell( 0, 6, ". done." )

pdfFile = 'tuto1.pdf'
pdf.output(pdfFile, 'F')

os.system("xdg-open " + pdfFile)