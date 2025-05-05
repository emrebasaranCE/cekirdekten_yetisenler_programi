## Why MongoDB & RabbitMQ?

### MongoDB  
- **Schema flexibility**  
  Air-quality readings arrive in JSON, with a variable set of pollutant parameters. MongoDB’s document model lets us store each reading “as-is” without rigid schemas or complex migrations.  
- **Time-series & geospatial support**  
  Built-in indexing for ISO-8601 timestamps and simple geospatial queries make it easy to fetch the last 24 hours of data, compute aggregates, or filter by latitude/longitude + radius.  
- **Scalability & high write throughput**  
  MongoDB handles bursts of frequent sensor writes, can shard as the dataset grows, and provides fast reads for dashboards and REST APIs.

### RabbitMQ  
- **Decoupling & reliability**  
  By publishing each incoming measurement to a durable queue, the collector, processor, and notifier stay loosely coupled—downstream services can crash or scale independently without losing messages.  
- **Acknowledgements & retries**  
  RabbitMQ’s ack/nack model ensures we only remove a message when it’s been successfully processed; failures automatically get retried.  
- **Multiple consumption patterns**  
  We use simple work‐queues for ingestion→processing, and pub/sub for anomalies→notifications, giving us flexibility to add new consumers (e.g. analytics, archiving) without touching the collector.
