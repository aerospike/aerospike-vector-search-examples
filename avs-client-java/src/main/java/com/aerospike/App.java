package com.aerospike;

public class App {

    public static void main(String[] args) {

        SetupUtils su = new SetupUtils();
        try {
            su.setup();
            su.testVectorSearchAsync();
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        } catch (Exception e) {
            throw new RuntimeException(e);
        }finally {
            su.close();
        }
    }
}
