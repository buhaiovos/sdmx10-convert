from io import TextIOWrapper
import xml.sax
import argparse
import pickle

replacements = {
    ':': '_colon_',
    '-': '_dash_',
    '.': '_dot_'
}

class CodelistIllegalIdsHandler(xml.sax.ContentHandler):

    def __init__(self, outfile: TextIOWrapper, outPickle: TextIOWrapper):
        xml.sax.ContentHandler.__init__(self)
        self.outfile = outfile
        self.outPickle = outPickle
        self.normalizedVals:set = set(())
        
    def dump(self):
        pickle.dump(self.normalizedVals, self.outPickle)

    def fixValue(self, attrValue: str) -> str:
        fixedValue = attrValue
        for search, replacement in replacements.items():
            fixedValue = fixedValue.replace(search, replacement) 
        if (fixedValue != attrValue):
            self.normalizedVals.add(attrValue)
        return fixedValue

    def startElement(self, name, attrs):
        self.outfile.write('<' + name)

        for attrName in attrs.keys():
            attrValue = attrs[attrName]
            attrValueSub = self.fixValue(attrValue) if (name == 'structure:Code' and attrName == 'value') else attrValue
            self.outfile.write(' {}="{}"'.format(attrName, attrValueSub))
            
        self.outfile.write('>')        

    def endElement(self, name):
        self.outfile.write('</{}>'.format(name))

    def characters(self, content):
        self.outfile.write(self.escapeText(content))
    
    def escapeText(self, text:str) -> str:
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&apos;')
    

def main():
    argumentsParser = argparse.ArgumentParser(description='Process XML file.')
    argumentsParser.add_argument('input_file', help='Input XML file')
    argumentsParser.add_argument('output_file', help='Output XML file')
    args = argumentsParser.parse_args()

    with (open(args.input_file, 'r') as input, 
          open(args.output_file, 'w') as out,
          open('normalized_values.pickle', 'wb') as normalizedOut):
        handler = CodelistIllegalIdsHandler(out, normalizedOut)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(input)
        handler.dump()

if __name__ == "__main__":
    main()