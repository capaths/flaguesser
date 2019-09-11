<template>
    <v-container>
        <v-text-field v-model="flagGuess" @keydown.enter="guessFlag"
                placeholder="Guess">
        </v-text-field>
        <v-row>
            <v-col v-for="i in Array(5).keys()" :key="i" style="height: 40px;width: 120px;" cols="2" justify="space-around" no-gutters>
                <v-row v-for="flag in getFlagSlice(i)" :key="flag.url">
                    <v-card  outlined tile style="height:90px;">
                        <v-img :src="flag" style="height:90px;"></v-img>
                    </v-card>
                </v-row>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
    export default {
        name: 'Flags',
        props: [
            'flags',
            'code',
        ],
        data() {
            return {
                flagGuess: '',
            };
        },
        beforeMount() {
            this.$options.sockets.onmessage = (message) => {
                const data = JSON.parse(message.data);
                if (data.type === 'event') {
                    if (data.event === 'guess') {
                    }
                }
            };
        },
        methods: {
            getFlagSlice(idx) {
                const start = idx * 4;
                const end = start + 4;

                const urls = Object.keys(this.flags);
                return urls.slice(start, end);
            },
            guessFlag() {
                if (!this.flagGuess) {
                    return;
                }

                this.$socket.sendObj({
                    method: 'guess_flag',
                    data: {
                        guess: this.flagGuess,
                    },
                });
                this.flagGuess = '';
            },
        },
    };
</script>

<style scoped>

</style>