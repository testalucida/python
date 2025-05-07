import pandas as pd
import xml.etree.ElementTree as et 

def test_1():
    xtree = et.parse("students.xml")
    xroot = xtree.getroot()

    df_cols = ["name", "email", "grade", "age"]
    rows = []

    for node in xroot: 
        s_name = node.attrib.get("name")
        s_mail = node.find("email").text if node is not None else None
        s_grade = node.find("grade").text if node is not None else None
        s_age = node.find("age").text if node is not None else None
        
        rows.append({"name": s_name,  "email": s_mail,  "grade": s_grade,  "age": s_age})
        
    out_df = pd.DataFrame(rows,  columns=df_cols)
    print( out_df )

def test_2(xml_file,  df_cols):
    """Parse the input XML file and store the result in a pandas 
    DataFrame with the given columns. 
    
    The first element of df_cols is supposed to be the identifier 
    variable, which is an attribute of each node element in the 
    XML data; other features will be parsed from the text content 
    of each sub-element. 
    """
    
    xtree = et.parse(xml_file)
    xroot = xtree.getroot()
    rows = []
    
    for node in xroot: 
        res = []
        res.append(node.attrib.get(df_cols[0]))
        #for el in df_cols[1:]:
        for el in df_cols:
            if node is not None and node.find(el) is not None:
                res.append(node.find(el).text)
            else: 
                res.append(None)
        rows.append({df_cols[i]: res[i] 
                     for i, _ in enumerate(df_cols)})
    
    out_df = pd.DataFrame(rows, columns=df_cols)
        
    return out_df    

if __name__ == "__main__":
    print( test_2( "students.xml",  ["name",  "email",  "grade",  "age"]) )
    #print( test_2( "calc_test_export.xhtml",  ["Name",  "Vorname",  "Alter"]) )
    
    
