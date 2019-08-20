<template>
    <v-card flat width="100%">
            <PlayerListItem
                    v-for="user in users"
                    :username="user.username"
                    :country="user.country"
                    :avatar="user.avatar"
                    :elo="user.elo"
                    :key="user.username"
            ></PlayerListItem>
    </v-card>
</template>

<script>
    import PlayerListItem from './PlayerListItem';

    export default {
        name: 'PlayerList',
        data() {
            return {
                users: [
                    {
                        username: 'capaths',
                        country: 'Chile',
                        avatar: 'https://www.belr.com/wp-content/uploads/2017/06/avatar-placeholder-generic-1.jpg',
                        elo: 1000,
                    },
                ],
            };
        },
        components: {PlayerListItem},
    };
</script>

<style scoped>

</style>