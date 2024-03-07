const Stats = {
    template: `
<div id="stats">
    <h1>Datasets</h1>
    <p>Total Images Indexed: <strong>{{totalImages}}</strong></p>
    <table class="table">
        <thead>
            <tr>
                <th>Name</th>
                <th>Indexed Images</th>
            </tr>
        </thead>
            <tr v-for="(count, dataset) in stats.datasets">
                <td >{{dataset}}</td>
                <td >{{count}}</td>
            </tr>
    </table>
</div>
  `,
    methods: {},
    async mounted() {
        try {
            const response = await axios.get('/rest/v1/stats')
            this.stats = response.data
            total = 0
            for (const dataset in this.stats.datasets) {
                total += this.stats.datasets[dataset]
            }
            this.totalImages = total
        } catch (err) {
            console.log(err)
        }
    },
    data() {
        return {
            stats: {},
            totalImages: 0
        }
    },
};
