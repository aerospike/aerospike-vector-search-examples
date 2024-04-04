const Home = {
  template: `
    <div>
        <h1 class="title">Aerospike Vector Search</h1>
        <div class="p-3 align-items-center justify-content-center">
        <p>
          <div class="d-flex flex-column flex-lg-row align-items-md-stretch justify-content-md-center gap-3 mb-4">
                <img class="proximus img-responsive center-block" src="/images/proximus.png"/>
          </div>
        </p>

        <p>
        This demo application provides semantic search for an included <a class="link-dark" href="https://archive.org/details/quotes_20230625">dataset of quotes</a>
        by indexing them using the <a class="link-dark" href="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2">MiniLM</a>
        model. This model generates vectors with semantic meaning 
        from each quote and stores them as vector embeddings in Aerospike. When a user
        submits a query, this demo app generates a vector embedding for the provided text
        and performs an Approximate Nearest Neighbor (<a class="link-dark"
        href="https://en.wikipedia.org/wiki/Nearest_neighbor_search#Approximate_nearest_neighbor">ANN</a>) 
        search using the Hierarchical Navigable Small World (<a class="link-dark"
        href="https://arxiv.org/pdf/1603.09320.pdf">HNSW</a>) algorithm to find relevant results.
        </p>

        <p>
            <div class="d-flex flex-column flex-lg-row align-items-md-stretch justify-content-md-center gap-3 mb-4">
            <router-link to="/search" class="btn btn-primary btn-lg bd-btn-lg btn-bd-primary d-flex align-items-center justify-content-center fw-semibold"
               role="button"
               aria-pressed="true">Get Started</router-link>
            </div>
        </p>
     </div>
  `
};
