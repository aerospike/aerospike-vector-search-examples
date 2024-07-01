package com.aerospike;

public class App {

    public static void main(String[] args) {

        try {
            SetupUtils.setup();
            SetupUtils.testVectorSearchAsync();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }
    }
}
