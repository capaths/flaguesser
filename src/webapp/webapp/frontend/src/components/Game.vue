<template>
    <v-container style="width:100%;">
        <Flags :flags="flags" :code="code" v-if="flags"></Flags>
        <PlayerList v-else></PlayerList>
        <v-dialog v-model="dialog" persistent max-width="290">
            <v-card>
                <v-card-title class="headline">Challenger approaches</v-card-title>
                <v-card-text>{{lastChallenge ? lastChallenge.sender : ""}}</v-card-text>
                <v-card-actions>
                    <div class="flex-grow-1"></div>
                    <v-btn color="green darken-1" text @click="rejectChallenge">Reject</v-btn>
                    <v-btn color="green darken-1" text @click="acceptChallenge">Accept</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </v-container>
</template>

<script>
    import Flags from './game/Flags'
    import PlayerList from './menu/PlayerList';

    export default {
        name: "Game",
        mounted() {
            this.$options.sockets.onmessage = (message) => {
                const data = JSON.parse(message.data);
                if (data.type === "event") {
                    if (data.event === 'challenge') {
                        this.lastChallenge = data.data;
                        this.dialog = true;
                    } else if (data.event === 'match_begins') {
                        this.code = data.data.code;
                        this.flags = {};
                        data.data.flags.forEach(flag => {
                            this.flags[flag] = false;
                        });
                    } else if (data.event === 'end_match') {
                        this.flags = undefined;
                        this.code = undefined;
                    }
                }
            };
        },
        components: {
            Flags,
            PlayerList,
        },
        data() {
            return {
                flags: undefined,
                roomCode: undefined,
                lastChallenge: undefined,
                code: undefined,
                dialog: false,
            };
        },
        methods: {
            acceptChallenge() {
                this.$socket.sendObj({
                    method: 'accept_challenge',
                    data: {
                        'challenger': this.lastChallenge.sender,
                        'code': this.lastChallenge.code,
                        'start_time': this.lastChallenge.start_time
                    }
                });
                this.dialog = false;
            },
            rejectChallenge() {
                this.dialog = false;
            },
        },
    };
</script>

<style scoped>

</style>