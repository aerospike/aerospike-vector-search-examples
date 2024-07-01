package com.aerospike;

import com.aerospike.vector.client.*;
import com.aerospike.vector.client.adminclient.AdminClient;
import com.aerospike.vector.client.dbclient.Client;
import com.aerospike.vector.client.dbclient.VectorSearchListener;
import com.aerospike.vector.client.internal.Conversions;
import com.aerospike.vector.client.internal.HostPort;
import com.aerospike.vector.client.internal.Projection;
import com.aerospike.vector.client.internal.VectorSearchQuery;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.IntBuffer;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

public class SetupUtils {
    private static final Logger LOG = LoggerFactory.getLogger(SetupUtils.class);
    private static final float TOLERANCE = 0.00001f;
    private static final String BASE_PATH = "src/main/resources/sift/";
    private static final int DIMENSIONS = 128;
    private static final int TRUTH_VECTOR_DIMENSIONS = 100;
    private static final int BASE_VECTOR_NUMBER = 10000;
    private static final int QUERY_VECTOR_NUMBER = 100;
    private static final String NAMESPACE = "test";
    private static final String INDEX_NAME = "searchtest";
    private static final String INDEX_SET_NAME = "demo";
    private static final String VECTOR_BIN_NAME = "v-test-bin";
    private static float[][] baseVectors;
    private static float[][] queryVectors;
    private static int[][] truthVectors;
    private static AdminClient adminClient;
    private static Client client;
    private static final int PROXIMUS_PORT = 10000;
    private static final String PROXIMUS_HOST = "localhost";

    /**
     * This function create index into the Aerospike vector DB and then inserts images, These images will be used to demonstrate vector search capabilities.
     * @throws Exception
     */
    public static void setup() throws Exception {
        baseVectors = loadBaseNumpy();
        queryVectors = loadQueryNumpy();
        truthVectors = loadTruthNumpy();

        // Instantiate admin client and VectorDB client. Admin client is primarily sued for adminsttrative purposes like index creation etc.
        // VectorDB client is used for inserting records, doing vector search etc.
        client = new Client(
                List.of(new HostPort(PROXIMUS_HOST, PROXIMUS_PORT, false)), "client-test", true);
        adminClient = new AdminClient(
                List.of(new HostPort(PROXIMUS_HOST, PROXIMUS_PORT, false)), "admin-test", true);


        // Create index
        adminClient.indexCreate(
                IndexId.newBuilder().setName(INDEX_NAME).setNamespace(NAMESPACE).build(),
                VECTOR_BIN_NAME, DIMENSIONS, VectorDistanceMetric.SQUARED_EUCLIDEAN,
                INDEX_SET_NAME,null , null, Map.of(), 60_000, 1_000);

        // Insert vectors
        for (int i = 0; i < baseVectors.length; i++) {
            client.putAsync(NAMESPACE, INDEX_SET_NAME, String.valueOf(i),
                    Map.of(VECTOR_BIN_NAME, baseVectors[i]), 0);
            if( i % 100 == 0) {
                Thread.sleep(1000);
            }
        }

        // Wait for records to get merged in the vector DB index.
        boolean allRecordsMerged = false;
        while (!allRecordsMerged) {
            long unmerged = adminClient.indexStatus(IndexId.newBuilder().setNamespace(NAMESPACE).setName(INDEX_NAME).build()).getUnmergedRecordCount();
            allRecordsMerged = unmerged == 0;
            LOG.warn("Waiting for index to merge, found unmerged {} records", unmerged);
            Thread.sleep(2000);
        }
    }

    /**
     * Demonstrate how to use async vector search
     * @throws Exception
     */
    public static void testVectorSearchAsync() throws Exception {
        AtomicLong counter = new AtomicLong();
        List<Neighbor>[] results = new ArrayList[queryVectors.length];
        for (int i = 0; i < queryVectors.length; i++) {
            SimpleListener listener = new SimpleListener(i, results, counter);
            if (i % 2 == 0) {
                VectorSearchQuery query = new VectorSearchQuery.Builder(NAMESPACE, INDEX_NAME,
                        Conversions.buildVectorValue(queryVectors[i]), 100).withProjection(Projection.getDefault()).build();
                client.vectorSearchAsync(query, listener);

            } else {
                VectorSearchQuery query = new VectorSearchQuery.Builder(NAMESPACE, INDEX_NAME,
                        Conversions.buildVectorValue(queryVectors[i]), 100)
                        .withHnswSearchParams(HnswSearchParams.newBuilder().setEf(80).build())
                        .withProjection(Projection.getDefault())
                        .build();
                client.vectorSearchAsync(query, listener);

            }
        }


        while (counter.get() != queryVectors.length) {
            LOG.warn("Waiting for async search completion, current counter: {}, expected: {}", counter.get(), queryVectors.length);
            Thread.sleep(1000);
        }

        List<Double> recallForEachQuery = computeRecall(Arrays.stream(results).toList());
        assertRecallMetrics(recallForEachQuery);
    }

    //----Utility functions-------

    private static float[][] loadBaseNumpy() throws Exception {
        String baseFilename = BASE_PATH + "siftsmall_base.fvecs";
        Path path = Paths.get(baseFilename);
        if (!Files.exists(path)) {
            throw new IOException("File does not exist: " + path.toAbsolutePath());
        }
        byte[] baseBytes = Files.readAllBytes(path);
        return parseSiftToFloatArray(baseBytes, BASE_VECTOR_NUMBER);
    }

    private static int[][] loadTruthNumpy() throws Exception {
        String truthFilename = BASE_PATH + "siftsmall_groundtruth.ivecs";
        byte[] truthBytes = Files.readAllBytes(Paths.get(truthFilename));
        return parseSiftToIntArray(truthBytes);
    }

    private static float[][] loadQueryNumpy() throws Exception {
        String queryFilename = BASE_PATH + "siftsmall_query.fvecs";
        byte[] queryBytes = Files.readAllBytes(Paths.get(queryFilename));
        return parseSiftToFloatArray(queryBytes, QUERY_VECTOR_NUMBER);
    }

    private static int[][] parseSiftToIntArray(byte[] byteBuffer) throws Exception {
        int[][] numpyArray = new int[QUERY_VECTOR_NUMBER][TRUTH_VECTOR_DIMENSIONS];
        int recordLength = (TRUTH_VECTOR_DIMENSIONS * 4) + 4;

        for (int i = 0; i < QUERY_VECTOR_NUMBER; i++) {
            int currentOffset = i * recordLength;
            ByteBuffer buffer = ByteBuffer.wrap(byteBuffer, currentOffset, recordLength);
            buffer.order(ByteOrder.LITTLE_ENDIAN);

            int readDim = buffer.getInt();
            if (readDim != TRUTH_VECTOR_DIMENSIONS) {
                throw new Exception("Failed to parse byte buffer correctly, expected dimension " + TRUTH_VECTOR_DIMENSIONS + ", but got " + readDim);
            }

            IntBuffer intBuffer = buffer.asIntBuffer();
            intBuffer.get(numpyArray[i]);
        }
        return numpyArray;
    }

    private static float[][] parseSiftToFloatArray(byte[] byteBuffer, int length) throws Exception {
        float[][] numpyArray = new float[length][DIMENSIONS];
        int recordLength = (DIMENSIONS * 4) + 4;

        for (int i = 0; i < length; i++) {
            int currentOffset = i * recordLength;
            ByteBuffer buffer = ByteBuffer.wrap(byteBuffer, currentOffset, recordLength);
            buffer.order(ByteOrder.LITTLE_ENDIAN);

            int readDim = buffer.getInt();
            if (readDim != DIMENSIONS) {
                throw new Exception("Failed to parse byte buffer correctly, expected dimension " + DIMENSIONS + ", but got " + readDim);
            }

            FloatBuffer floatBuffer = buffer.asFloatBuffer();
            floatBuffer.get(numpyArray[i]);
        }
        return numpyArray;
    }

    private static void assertRecallMetrics(List<Double> recallForEachQuery) {
        double recallSum = recallForEachQuery.stream().mapToDouble(Double::doubleValue).sum();
        double average = recallSum / recallForEachQuery.size();

        if (average < 0.95) {
            throw new RuntimeException(String.format("Average recall is too low: %f", average));
        }

        for (Double recall : recallForEachQuery) {
            if (recall < 0.9) {
                throw new RuntimeException(String.format("Recall is too low for a query: %f", recall));
            }
        }
    }

    private static List<Double> computeRecall(List<List<Neighbor>> results) {
        List<Double> recallForEachQuery = new ArrayList<>();

        for (int i = 0; i < truthVectors.length; i++) {
            final int[] truth = truthVectors[i];
            int truePositive = 0;
            int falseNegative = 0;
            List<float[]> binList = new ArrayList<>();

            for (Neighbor result : results.get(i)) {
                List<Float> floatList = result.getRecord().getFields(0).getValue().getVectorValue().getFloatData().getValueList();
                float[] floats = new float[floatList.size()];
                for (int j = 0; j < floatList.size(); j++) {
                    floats[j] = floatList.get(j);
                }
                binList.add(floats);
            }

            for (int idx : truth) {
                float[] vector = baseVectors[idx];
                if (binList.stream().anyMatch(searchResult -> areEqual(searchResult, vector))) {
                    truePositive++;
                } else {
                    falseNegative++;
                }
            }

            double recall = truePositive / (double) (truePositive + falseNegative);
            recallForEachQuery.add(recall);
        }

        return recallForEachQuery;
    }

    private static boolean areEqual(float[] array1, float[] array2) {
        if (array1 == null || array2 == null) {
            return array1 == array2;
        }

        if (array1.length != array2.length) {
            return false;
        }

        for (int i = 0; i < array1.length; i++) {
            if (Math.abs(array1[i] - array2[i]) > TOLERANCE) {
                return false;
            }
        }
        return true;
    }

    private static class SimpleListener implements VectorSearchListener {
        List<Neighbor>[] results;
        int idx;
        AtomicLong counter;

        public SimpleListener(int idx, List<Neighbor>[] results, AtomicLong counter) {
            this.results = results;
            this.idx = idx;
            this.counter = counter;
        }

        List<Neighbor> result = new ArrayList<>();

        @Override
        public void onNext(Neighbor neighbor) {
            result.add(neighbor);
        }

        @Override
        public void onComplete() {
            results[idx] = result;
            counter.incrementAndGet();
        }

        @Override
        public void onError(Throwable e) {
            LOG.warn("Error in listener {}", e);
        }
    }
}
