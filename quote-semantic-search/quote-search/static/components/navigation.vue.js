const Navigation = {
    template: `
        <div class="container">
            <header class="d-flex flex-wrap justify-content-center py-3 mb-4 border-bottom">
                <a href="." class="logo d-flex align-items-center mb-3 mb-md-0 me-md-auto text-dark text-decoration-none">
                    <img class="bi me-2"
                         src="/images/aerospike-logo.png">
                </a>

                <ul class="nav nav-pills">
                     <li>
                          <router-link exact active-class="active" class="nav-link" to="/">
                                Home
                          </router-link>
                    </li>
                    <li>
                          <router-link exact active-class="active" class="nav-link" to="/search">
                                Search
                          </router-link>
                    </li>
                    <li>
                          <router-link exact active-class="active" class="nav-link" to="/stats">
                                Stats
                          </router-link>
                    </li>
                </ul>
            </header>
        </div>
  `,
    data() {
        return {
            errors: []
        }
    },
    computed: {},
};
