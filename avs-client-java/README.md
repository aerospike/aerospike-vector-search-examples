# Proximus Java Client

This project demonstrates the use of Aerospike's vector database capabilities with `AdminClient` and `Client` classes. The project is configured with Maven and includes sample data for testing vector search functionalities.

## Overview 
 - This is a demo project to illustrate how can a simple image search application can be built with Aerospike Vector database using vector database java client.

## Prerequisites

- Java 21
- An AVS **0.9.0** running locally and accessible from the application. If the AVS is not available locally then update `HOSTNAME`  and `PORT` In `SetupUtils.java`, other connection related information can be also updated in this file.     

## Build and run
 - run `mvn package` command from `avs-client-java` directory. 
 - run `java -jar target/avs-client-java-demo-0.3.0.jar`

## Project Structure

```
client-test/
        ├── src/
        │ ├── main/
        │ │ ├── java/
        │ │ │ └── com/
        │ │ │ └── aerospike/
        │ │ │ ├── App.java
        │ │ │ └── SetupUtils.java
        │ └── resources/
        │   └── sift/
        │       ├── siftsmall_base.fvecs
        │       ├── siftsmall_groundtruth.ivecs
        │       └── siftsmall_query.fvecs
        └── pom.xml
```

## Maven Configuration

Necessary `pom.xml` configuration for the project:

```xml
    <dependencies>   
        <!-- avs java client dependency -->
        <dependency>
            <groupId>com.aerospike</groupId>
            <artifactId>avs-client-java</artifactId>
            <version>0.3.0</version>
        </dependency>
    </dependencies>
```


## Application Code
`App.java` This class initializes the setup and test methods for the vector database.

### SetupUtils.java 
  - This class handles the setup of the vector database and the asynchronous vector search tests. 
  - What it does: Load Data:
     - Loads base vectors, query vectors, and ground truth vectors from files. 
     - Initialize Clients:
        - Sets up `Client` and `AdminClient` using the provided Aerospike host(`localhost`) and port (`10000`). 
     - Create Index: Creates an index in the Aerospike database for storing vector data. 
     - Insert Vectors: Inserts the base vectors into the Aerospike database. 
     - Wait for Merge: Waits until all records are merged in the index.
       - Perform Vector Search: Executes asynchronous vector searches using the query vectors. 
       - Computes recall metrics to evaluate the search results. 
       
       - Key Methods:
          - `setup(String host, int port)`: Handles data loading, client initialization, index creation, vector insertion, and waiting for records to merge.
          -  `testVectorSearchAsync()`: Executes the vector search tests and computes recall metrics.


### Javadocs
Please refer to the [javadocs](https://javadoc.io/doc/com.aerospike/avs-client-java/latest/index.html) for more details.

