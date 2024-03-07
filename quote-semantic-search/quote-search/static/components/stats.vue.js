const Stats = {
    template: `
<div id="stats">
  <h1>Datasets</h1>
        <p>Total Quotes Indexed: <strong>{{totalQuotes}}</strong></p>
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
            this.totalQuotes = total
        } catch (err) {
            console.log(err)
        }
    },
    data() {
        return {
            stats: {},
            totalQuotes: 0
        }
    },
};
