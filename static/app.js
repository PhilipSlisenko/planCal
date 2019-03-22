const app = new Vue({
	el: '#app',
	data: {
	    scheduleUrls: [{
			url: "http://planzajec.uek.krakow.pl/index.php?typ=G&id=116071&okres=1"
		}],
		groups:[],
		stateOfApp: "provideUrls" //"provideUrls" //"pickClasses"
	},
	computed: {
		filledUrls: function () {
			return this.scheduleUrls.reduce((sum, obj) => {
				return Boolean(obj.url) ? sum + 1 : sum
			}, 0);
		},
		nonEmptyUrls: function () {
			let nonEmptyStillObj = this.scheduleUrls.filter((obj) =>
				Boolean(obj.url));
			return nonEmptyStillObj.map((obj) => obj.url);
		},
		showUrlPicker: function () {
			if (["provideUrls"].includes(this.stateOfApp)) {
				return true;
			} else {
				return false;
			}
		},
		showClassPicker: function () {
			if (["pickClasses"].includes(this.stateOfApp)) {
				return true;
			} else {
				return false;
			}
		},
	},
	watch: {

	},
	methods: {
		moreUrls: function () {
			this.scheduleUrls.push({
				url: ""
			});
		},
		getGroups: function () {
		    let url = window.getClassesUrl;
			let urls = this.nonEmptyUrls;
			let parameters = urls.map((str) => "urls=" + encodeURIComponent(str));
			parameters = parameters.join('&');
			let endpoint = url + "?" + parameters;
			console.log(url);
			console.log(urls);
			console.log(endpoint);
			fetch(endpoint)
				.then(
					(response) => {
						if (response.ok) {
							return response.json()
						};
						throw new Error('Request failed!');
					},
					(networkError) => {
						console.log(networkError.message);
					})
				.then((jsonResponse) => {
					this.groups = jsonResponse;
					this.stateOfApp = "pickClasses";
				});
		},
		getCal: function () {
			let url = window.genCalUrl;
			fetch(url, {
					headers: {
						'Content-Type': 'application/json'
					},
					method: 'POST',
					body: JSON.stringify(this.groups.map((g) => {
						return {
							'classes': g['classes'].filter(c => c['checked']).map(c => c['key']),
							'url': g['url']
						}
					}))
				})
				.then(
					(response) => {
						if (response.ok) {
							return response.json()
						};
						throw new Error('Request failed!');
					},
					(networkError) => {
						console.log(networkError.message);
					})
				.then((jsonResponse) => {
					console.log('http://127.0.0.1:5000/download_cal/' + jsonResponse);
					window.location.assign('http://127.0.0.1:5000/download_cal/' + jsonResponse)
				});
		}
	}
});
