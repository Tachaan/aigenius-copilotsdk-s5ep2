using Microsoft.EntityFrameworkCore;
using AgentHQDemo.Api.Models;

namespace AgentHQDemo.Api.Data;

public class RetailDbContext(DbContextOptions<RetailDbContext> options) : DbContext(options)
{
    public DbSet<Transaction> Transactions => Set<Transaction>();
    public DbSet<CustomerSegment> Segments => Set<CustomerSegment>();
}
