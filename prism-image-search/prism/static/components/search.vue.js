const Search = {
    template: `
<div>
    <form v-on:submit.prevent="submitForm">
        <div class="mb">
            <label class="form-label" for="textInput">Enter text for similarity search</label>
        </div>
        <div class="input-group">
            <input type="text" id="textInput" v-model="textInput" class="form-control" placeholder="Search">
            <div class="input-group-btn">
                <button :disabled="!textInput" class="btn btn-primary" type="submit">
                    Search
                </button>
            </div>
        </div>
    </form>

    <div v-if="url" >
        <h4 style="padding: 10px">Searching for </h4>
        <img id="preview" v-if="url" :src="url" />
    </div>

    <div style="padding: 10px" id="errors" v-if="errors.length > 0" >
        <p v-for="error in errors" class="error">{{error}}</p>
    </div>

    <div style="padding: 30px" id="no-results" v-if="results.length == 0 && timeTaken" >
    <p>No results found. Server Query Time: <strong>{{timeTaken}}</strong> ms, Total Time: <strong>{{totalTimeTaken}}</strong> ms</p>
    </div>
    <div style="padding: 30px" id="results" v-if="results.length > 0" >
        <p>Found <strong>{{results.length}}</strong> results. Server Query Time: <strong>{{timeTaken}}</strong> ms, Total Time: <strong>{{totalTimeTaken}}</strong> ms</p>
        <div v-for="result in results" class="responsive">
            <div class="gallery">
                <img class="search-result"
                     :src="'/images/data' + result.relative_path"
                     :alt="result.image_name" :title="result.relative_path"/>
                <div class="input-group-btn">
                    <button @click="findSimilar(result.image_id, result.relative_path)" class="btn btn-outline-secondary btn-sm search-similar" type="submit">
                        Search
                    </button>
                </div>
            </div>
            </div>
        </div>
    </div>
</div>
    `,
    methods: {
        handleFileUpload(event) {
            this.file = event.target.files[0];
        },
        processResponse(res) {
            //Perform Success Action
            this.errors = []
            this.results = res.data.results;
            this.timeTaken = Number((res.data.timeTaken * 1000)).toFixed(2);
            this.totalTimeTaken = Number((Date.now() - startTime).toFixed(2));
        },
        submitForm() {
            let formData = new FormData();
            // this.url = URL.createObjectURL(this.file);
            formData.append('text', this.textInput);
            startTime = Date.now()
            axios.post('/rest/v1/search', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })
                .then(this.processResponse)
                .catch((error) => {
                    this.errors = [error];
                    this.results = [];
                    this.timeTaken = 0;
                }).finally(() => {
                //Perform action in always
            });
        },
        findSimilar(image_id, relative_path) {
            this.url = 'images/data' + relative_path
            startTime = Date.now()
            axios.get('/rest/v1/search_by_id', {params: {image_id: image_id}})
                .then(this.processResponse)
                .catch((error) => {
                    this.errors = [error]
                    this.results = [];
                    this.timeTaken = 0;
                }).finally(() => {
                //Perform action in always
            });
        }
    },
    data() {
        return {
            textInput: '',
            url: '',
            results: [],
            timeTaken: '',
            totalTimeTaken: '',
            errors: []
        }
    },
}
