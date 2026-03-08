from rest_framework import serializers
from Clans.models import Clan, Members


class ClansSerializer(serializers.ModelSerializer):
    class Meta:
        models = Clan
        fields = [
            "name",
            "discription",
            "visibility",
            "activity",
            "member_count",
            "created_at"
        ]


class UserJoinedClansSerializer(serializers.ModelSerializer):
    clan_data = ClansSerializer()
    class Meta:
        models = Members
        fields = [
            "clan_data",
            "roles",
            "joined_at"
        ]

class CreateClanSerializer(serializers.Serializer):
    name = serializers.CharField(min_length=3, max_length=100, required=True)
    discription = serializers.CharField(max_length=500, required=False)
    visibility = serializers.ChoiceField(choices=[
        ('private', 'private'),
        ('public', 'public')
    ], required=False)
    creator = serializers.IntegerField(required=True)
    joining_code = serializers.CharField(min_length=6, max_length=100, required=False)

    def validate_name(self, name):
        name = name.strip()
        if Clan.objects.filter(name__iexact=name):
            raise serializers.ValidationError(f"Clan name alredy taken")
        
        return name

    def validate(self, data):
        visibility = data.get('visibility')
        joining_code = data.get('joining_code')

        if visibility == 'private':
            if not joining_code:
                raise serializers.ValidationError("Private clans must have a joining code")
            data['joining_code'] = joining_code.strip()
        elif visibility == 'public' and joining_code:
            raise serializers.ValidationError("Public clans cannot have a joining code")

        return data

