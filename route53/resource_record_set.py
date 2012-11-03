from route53.change_set import ChangeSet

class ResourceRecordSet(object):
    """
    A Resource Record Set is an entry within a Hosted Zone. These can be
    anything from TXT entries, to A entries, to CNAMEs.

    .. warning:: Do not instantiate this directly yourself. Go through
        one of the methods on:py:class:``route53.connection.Route53Connection`.
    """

    # Override this in your sub-class.
    rrset_type = None

    def __init__(self, connection, zone_id, name, ttl, records):
        """
        :param Route53Connection connection: The connection instance that
            was used to query the Route53 API, leading to this object's
            creation.
        :param str zone_id: The zone ID of the HostedZone that this
            resource record set belongs to.
        :param str name: The fully qualified name of the resource record set.
        :param int ttl: The time-to-live. A Aliases have no TTL, so this can
            be None in that case.
        :param list records: A list of resource record strings. For some
            types (A entries that are Aliases), this is an empty list.
        """

        self.connection = connection
        self.zone_id = zone_id
        self.name = name
        self.ttl = int(ttl) if ttl else None
        self.records = records

        # Keep track of the initial values for this record set. We use this
        # to detect changes that need saving.
        self._initial_vals = dict(
            connection=connection,
            zone_id=zone_id,
            name=name,
            ttl=ttl,
            records=records,
        )

    def __str__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.name)

    @property
    def hosted_zone(self):
        """
        Queries for this record set's HostedZone.

        :rtype: HostedZone
        :returns: The matching HostedZone for this record set.
        """

        return self.connection.get_hosted_zone_by_id(self.zone_id)

    def is_modified(self):
        """
        Determines whether this record set has been modified since retrieval.

        :rtype: bool
        :returns: ``True` if the record set has been modified,
            and ``False`` if not.
        """

        for key, val in self._initial_vals:
            if getattr(self, key) != val:
                # One of the initial values doesn't match, we know
                # this object has been touched.
                return True

        return False

    def delete(self):
        """
        Deletes this record set.
        """

        cset = ChangeSet(connection=self.connection, hosted_zone_id=self.zone_id)
        cset.add_change('DELETE', self)

        return self.connection._change_resource_record_sets(cset)

    def save(self):
        """
        Saves any changes to this record set.
        """

        # TODO: Copy changes to self._initial_vals.
        pass

    def is_alias_record_set(self):
        """
        Checks whether this is an A record in Alias mode.

        :rtype: bool
        :returns: ``True`` if this is an A record in Alias mode, and
            ``False`` otherwise.
        """

        # AResourceRecordSet overrides this. Everyone else is False.
        return False


class AResourceRecordSet(ResourceRecordSet):
    """
    Specific A record class. There are two kinds of A records:

    * Regular A records.
    * Alias A records. These point at an ELB instance instead of an IP.
    """

    rrset_type = 'A'

    def __init__(self, alias_hosted_zone_id=None, alias_dns_name=None, *args, **kwargs):
        """
        :keyword str alias_hosted_zone_id: Alias A records have this specified.
            It appears to be the hosted zone ID for the ELB the Alias points at.
        :keyword str alias_dns_name: Alias A records have this specified. It is
            the DNS name for the ELB that the Alias points to.
        """

        super(AResourceRecordSet, self).__init__(*args, **kwargs)

        self.alias_hosted_zone_id = alias_hosted_zone_id
        self.alias_dns_name = alias_dns_name

        # Keep track of the initial values for this record set. We use this
        # to detect changes that need saving.
        self._initial_vals.update(
            dict(
                alias_hosted_zone_id=alias_hosted_zone_id,
                alias_dns_name=alias_dns_name,
            )
        )

    def is_alias_record_set(self):
        """
        Checks whether this is an A record in Alias mode.

        :rtype: bool
        :returns: ``True`` if this is an A record in Alias mode, and
            ``False`` otherwise.
        """

        return self.alias_hosted_zone_id or self.alias_dns_name


class AAAAResourceRecordSet(ResourceRecordSet):
    """
    Specific AAAA record class.
    """

    rrset_type = 'AAAA'


class CNAMEResourceRecordSet(ResourceRecordSet):
    """
    Specific CNAME record class.
    """

    rrset_type = 'CNAME'


class MXResourceRecordSet(ResourceRecordSet):
    """
    Specific MX record class.
    """

    rrset_type = 'MX'


class NSResourceRecordSet(ResourceRecordSet):
    """
    Specific NS record class.
    """

    rrset_type = 'NS'


class PTRResourceRecordSet(ResourceRecordSet):
    """
    Specific PTR record class.
    """

    rrset_type = 'PTR'


class SOAResourceRecordSet(ResourceRecordSet):
    """
    Specific SOA record class.
    """

    rrset_type = 'SOA'


class SPFResourceRecordSet(ResourceRecordSet):
    """
    Specific SPF record class.
    """

    rrset_type = 'SPF'


class SRVResourceRecordSet(ResourceRecordSet):
    """
    Specific SRV record class.
    """

    rrset_type = 'SRV'


class TXTResourceRecordSet(ResourceRecordSet):
    """
    Specific TXT record class.
    """

    rrset_type = 'TXT'
