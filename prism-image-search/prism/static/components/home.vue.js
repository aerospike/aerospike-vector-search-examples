const Home = {
    template: `
    <div>
        <h1 class="title">Proximus Image search</h1>
        <div class="p-3 align-items-center justify-content-center">
        <p>
          <div class="d-flex flex-column flex-lg-row align-items-md-stretch justify-content-md-center gap-3 mb-4">
                <img class="proximus img-responsive center-block" src="/images/proximus.png" alt="Proximus"/>
          </div>
        </p>

        <p>
            <a class="link-dark" href="https://github.com/citrusleaf/proximus"><strong>Aerospike Proximus<strong></strong></a> is a
            highly scalable and fast <strong>Vector database</strong> that can store and query vector data.
            Proximus supports Approximate Nearest Neighbor (<a class="link-dark"
                        href="https://en.wikipedia.org/wiki/Nearest_neighbor_search#Approximate_nearest_neighbor">ANN</a>)
            search using proximity graph indices. See <a class="link-dark"
                                                         href="https://arxiv.org/pdf/1603.09320.pdf">HNSW</a>.
        </p>

        <p>
            This demo application uses image embedding models for image encoding and Proximus to store and
            perform ANN queries on image vectors to find images similar to an input image.

            <div class="d-flex flex-column flex-lg-row align-items-md-stretch justify-content-md-center gap-3 mb-4">
            <router-link to="/search" class="btn btn-primary btn-lg bd-btn-lg btn-bd-primary d-flex align-items-center justify-content-center fw-semibold"
               role="button"
               aria-pressed="true">Get Started</router-link>
            </div>
        </p>
     </div>
  `
};
