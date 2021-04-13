import argparse
import json
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.value_provider import StaticValueProvider
from google.cloud import storage
from smart_open import open

class ReadFile(beam.DoFn):

    def __init__(self, input_path):
        self.input_path = input_path

    def start_bundle(self):
        self.client = storage.Client()

    def process(self, something):
        
        logging.info(self.input_path.get())

        clear_data = []
        with open(self.input_path.get()) as fin:
            for line in fin:
                data = json.loads(line)
                
                for elems in data['annotation_results']:
                  for item in elems['object_annotations']:

                    clear_data.append({
                      'description': item['entity']['description'],
                      'time' : 0
                    })

        yield clear_data

class DataflowOptions(PipelineOptions):

    @classmethod
    def _add_argparse_args(cls, parser):
        parser.add_value_provider_argument('--input', type=str)

    def run(self, argv=None):
        pipeline_options = PipelineOptions()
        user_options = pipeline_options.view_as(DataflowOptions)

        with beam.Pipeline(options=pipeline_options) as pipeline:
            (pipeline
                | 'Start' >> beam.Create([None])
                | 'Read JSON' >> beam.ParDo(ReadFile(user_options.input))
                | 'Write to BigQuery' >> beam.io.Write(beam.io.WriteToBigQuery('apt-subset-310017:bq_object_detection_store.data_store', schema="line:STRING"))
            )

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    r = DataflowOptions()
    r.run()
