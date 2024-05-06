import csv
import xml.sax
import argparse
import pickle
import parse_date as dateParser

from io import BufferedReader, TextIOWrapper

replacements = {
    ':': '_colon_',
    '-': '_dash_',
    '.': '_dot_'
}

def normalizeValue(value:str) -> str:
        fixedValue = value
        for search, replacement in replacements.items():
            fixedValue = fixedValue.replace(search, replacement) 
        return fixedValue
    
def mapTimePeriod(freq:str, period:str) -> str:
    #parse_date output is year, quarter, month, week
    parsedDate = dateParser.parse(freq)
    match (period):
        case '8' | '9': 
            #daily
            return f'{parsedDate.year}-D{parsedDate.dayOfYear:03d}'
        case '19' | '20' | '21' | '67':  
            #weekly
            return f'{parsedDate.year}W{parsedDate.dayOfYear:02d}'   
        case '129': 
            #monthly
            return f'{parsedDate.year}-{parsedDate.month:02d}'
        case '162': 
            #quarterly
            return f'{parsedDate.year}Q{parsedDate.quarter}'
        case '203': 
            #yearly
            return f'{parsedDate.year}'
        case _:
            raise Exception("Unsupported freq: " + period)

class XmlToCsvConverter(xml.sax.ContentHandler):
    
    def __init__(self, outfile:TextIOWrapper, normalizedPickle:BufferedReader):
        xml.sax.ContentHandler.__init__(self)
        self.outfile = outfile
        self.firstRow = True
        self.csvWriter = csv.writer(outfile)
        self.currentSeries = []
        self.currentObs = []
        self.currentTimePeriod = ''
        self.currentFreq = ''
        self.header = []
        self.normalizedValues:set = pickle.load(normalizedPickle)
        print(self.normalizedValues)
        
    def processValue(self, value:str) -> str:
        if (value in self.normalizedValues):
            return normalizeValue(value)
        return value
    
    def startElement(self, name, attrs):
        if (name == 'kf:Series'):
            for attrName in attrs.keys():
                attrValue = attrs[attrName]
                
                if (attrName == 'FREQ'):
                    self.currentFreq = attrValue
                
                if (self.firstRow):
                    self.header.append(attrName)
                self.currentSeries.append(self.processValue(attrValue))
        
        elif (name == 'frb:Obs'):
            for attrName in attrs.keys():
                attrValue = attrs[attrName]
                
                if (attrName == 'TIME_PERIOD'):
                    self.currentTimePeriod = attrValue
                
                if (self.firstRow):
                    self.header.append(attrName)
                
                self.currentObs.append(self.processValue(attrValue))

    
    def endElement(self, name):
        if (name == 'frb:Obs'):
            if(self.firstRow):
                self.header.append('TIME_PERIOD_MAPPED')
                self.csvWriter.writerow(self.header)
                self.firstRow = False
                self.header.clear()
                
            mappedTimePeriod = mapTimePeriod(self.currentTimePeriod, self.currentFreq)
            
            self.currentObs.append(mappedTimePeriod)
            self.csvWriter.writerow(self.currentSeries + self.currentObs)
            self.currentObs.clear()
            
        if (name == 'kf:Series'):
            self.currentSeries.clear()

    
    def characters(self, _):
        return
    
    
def main():
    argumentsParser = argparse.ArgumentParser(description='Process XML file.')
    argumentsParser.add_argument('input_file', help='Input XML file')
    argumentsParser.add_argument('output_file', help='Output XML file')
    args = argumentsParser.parse_args()

    with (open(args.input_file, 'r') as input, 
          open(args.output_file, 'w', newline='') as out,
          open('normalized_values.pickle', 'rb') as normalizedPickle):
        handler = XmlToCsvConverter(out, normalizedPickle)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(input)

if __name__ == "__main__":
    main()