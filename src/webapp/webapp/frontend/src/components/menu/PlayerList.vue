<template>
    <v-card flat outlined>
        <v-list dense width="100%" max-height="100%" id="chatList">
            <PlayerListItem
                    v-for="user in users"
                    :username="user.username"
                    :country="user.country"
                    :avatar="user.avatar"
                    :elo="user.elo"
                    :key="user.username"
            ></PlayerListItem>
        </v-list>
        <v-btn @click.prevent="reloadOnlineUsers">
            Refresh
        </v-btn>
    </v-card>
</template>

<script>
    import {userService} from "../../_services/player.service";

    import PlayerListItem from './PlayerListItem';
    import {mapState} from 'vuex';

    export default {
        name: 'PlayerList',
        data() {
            return {
                users: [
                ],
            };
        },
        methods: {
            reloadOnlineUsers() {
                userService.getOnlineUsers()
                    .then(response => {
                        this.users = Object.values(response.data);
                        this.users = this.users.filter(user => user.username !== this.user.username);
                    });
            }
        },
        mounted() {
            this.reloadOnlineUsers();
        },
        computed: {
            ...mapState('account', ['user']),
        },
        components: {PlayerListItem},
    };
</script>

<style scoped>

</style>